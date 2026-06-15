import os
import hashlib
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        load_dotenv()
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'developer')
        self.password = os.getenv('DB_PASSWORD', 'Taller2026')
        self.database = os.getenv('DB_NAME', 'taller')

    def get_connection(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except Error as e:
            print(f"Error de conexión: {e}")
            return None

    def execute_query(self, query, params=None):
        """Ejecuta INSERT, UPDATE, DELETE. Retorna (exito, mensaje, lastrowid)"""
        conn = self.get_connection()
        if not conn:
            return False, "Error de conexión", None
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return True, "Operación exitosa", cursor.lastrowid
        except Error as e:
            return False, f"Error: {e}", None
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, query, params=None):
        """Ejecuta SELECT y retorna lista de diccionarios"""
        conn = self.get_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Error en fetch_all: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def verify_user(self, username, password):
        conn = self.get_connection()
        if not conn:
            return False, "Error de conexión", None
        cursor = conn.cursor()
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            query = "SELECT password, rol FROM usuarios WHERE username = %s"
            cursor.execute(query, (username,))
            resultado = cursor.fetchone()
            if resultado:
                password_bd = resultado[0]
                if isinstance(password_bd, bytes):
                    password_bd = password_bd.decode('utf-8')
                rol = resultado[1] if len(resultado) > 1 else "mecanico"
                if password_hash == password_bd:
                    return True, "Login exitoso", rol
                else:
                    return False, "Contraseña incorrecta", None
            else:
                return False, "Usuario no existe", None
        except Error as e:
            return False, f"Error: {e}", None
        finally:
            cursor.close()
            conn.close()

    def listar_clientes(self):
        return self.fetch_all("SELECT id, cedula, nombre, telefono, email FROM clientes ORDER BY id")

    def agregar_cliente(self, cedula, nombre, telefono, email):
        if self.fetch_all("SELECT id FROM clientes WHERE cedula = %s", (cedula,)):
            return False, "La cédula ya existe", None
        query = "INSERT INTO clientes (cedula, nombre, telefono, email) VALUES (%s, %s, %s, %s)"
        return self.execute_query(query, (cedula, nombre, telefono, email))

    def actualizar_cliente(self, id_cliente, cedula, nombre, telefono, email):
        duplicado = self.fetch_all("SELECT id FROM clientes WHERE cedula = %s AND id != %s", (cedula, id_cliente))
        if duplicado:
            return False, "La cédula ya está en uso por otro cliente"
        query = "UPDATE clientes SET cedula=%s, nombre=%s, telefono=%s, email=%s WHERE id=%s"
        return self.execute_query(query, (cedula, nombre, telefono, email, id_cliente))

    def eliminar_cliente(self, id_cliente):
        query = "DELETE FROM clientes WHERE id=%s"
        return self.execute_query(query, (id_cliente,))

    def obtener_cliente_por_id(self, id_cliente):
        res = self.fetch_all("SELECT id, cedula, nombre, telefono, email FROM clientes WHERE id=%s", (id_cliente,))
        return res[0] if res else None

    def listar_vehiculos(self):
        query = """
            SELECT v.id, v.placa, v.marca, v.modelo, c.nombre as cliente_nombre, v.cliente_id
            FROM vehiculos v
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.id
        """
        return self.fetch_all(query)

    def listar_clientes_combobox(self):
        return self.fetch_all("SELECT id, nombre FROM clientes ORDER BY nombre")

    def agregar_vehiculo(self, placa, marca, modelo, cliente_id):
        if self.fetch_all("SELECT id FROM vehiculos WHERE placa = %s", (placa,)):
            return False, "La placa ya existe", None
        query = "INSERT INTO vehiculos (placa, marca, modelo, cliente_id) VALUES (%s, %s, %s, %s)"
        return self.execute_query(query, (placa.upper(), marca, modelo, cliente_id))

    def actualizar_vehiculo(self, id_vehiculo, placa, marca, modelo, cliente_id):
        duplicado = self.fetch_all("SELECT id FROM vehiculos WHERE placa = %s AND id != %s", (placa, id_vehiculo))
        if duplicado:
            return False, "La placa ya está en uso por otro vehículo"
        query = "UPDATE vehiculos SET placa=%s, marca=%s, modelo=%s, cliente_id=%s WHERE id=%s"
        return self.execute_query(query, (placa.upper(), marca, modelo, cliente_id, id_vehiculo))

    def eliminar_vehiculo(self, id_vehiculo):
        query = "DELETE FROM vehiculos WHERE id=%s"
        return self.execute_query(query, (id_vehiculo,))

    def obtener_vehiculo_por_id(self, id_vehiculo):
        res = self.fetch_all("SELECT id, placa, marca, modelo, cliente_id FROM vehiculos WHERE id=%s", (id_vehiculo,))
        return res[0] if res else None