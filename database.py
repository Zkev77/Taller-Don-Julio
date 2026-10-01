import os
import hashlib
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from utilidades import BAJO_STOCK

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._cargar_configuracion()
        return cls._instance

    def _cargar_configuracion(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
        self.servidor = os.getenv('DB_HOST', 'localhost')
        self.usuario = os.getenv('DB_USER', '')
        self.contrasena = os.getenv('DB_PASSWORD', '')
        self.base_datos = os.getenv('DB_NAME', 'taller')

    def obtener_conexion(self):
        if not self.usuario or not self.contrasena:
            print("Error de configuración: defina DB_USER y DB_PASSWORD en el archivo .env")
            return None
        try:
            return mysql.connector.connect(
                host=self.servidor,
                user=self.usuario,
                password=self.contrasena,
                database=self.base_datos
            )
        except Error as e:
            print(f"Error de conexión: {e}")
            return None

    def ejecutar_consulta(self, consulta, parametros=None):
        conexion = self.obtener_conexion()
        if not conexion:
            return False, "Error de conexión", None
        cursor = conexion.cursor()
        try:
            cursor.execute(consulta, parametros or ())
            conexion.commit()
            return True, "Operación exitosa", cursor.lastrowid
        except Error as e:
            return False, f"Error: {e}", None
        finally:
            cursor.close()
            conexion.close()

    def obtener_todos(self, consulta, parametros=None):
        conexion = self.obtener_conexion()
        if not conexion:
            return None
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(consulta, parametros or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Error en obtener_todos: {e}")
            return None
        finally:
            cursor.close()
            conexion.close()

    def verificar_usuario(self, nombre_usuario, contrasena):
        conexion = self.obtener_conexion()
        if not conexion:
            return False, "Error de conexión", None
        cursor = conexion.cursor()
        try:
            hash_contrasena = hashlib.sha256(contrasena.encode()).hexdigest()
            consulta = "SELECT password, rol FROM usuarios WHERE username = %s"
            cursor.execute(consulta, (nombre_usuario,))
            resultado = cursor.fetchone()
            if resultado:
                contrasena_bd = resultado[0]
                if isinstance(contrasena_bd, bytes):
                    contrasena_bd = contrasena_bd.decode('utf-8')
                rol = resultado[1] if len(resultado) > 1 else "mecanico"
                if hash_contrasena == contrasena_bd:
                    return True, "Login exitoso", rol
                else:
                    return False, "Contraseña incorrecta", None
            else:
                return False, "Usuario no existe", None
        except Error as e:
            return False, f"Error: {e}", None
        finally:
            cursor.close()
            conexion.close()

    def listar_clientes(self):
        return self.obtener_todos("SELECT id, cedula, nombre, telefono, email FROM clientes ORDER BY id")

    def agregar_cliente(self, cedula, nombre, telefono, email):
        if self.obtener_todos("SELECT id FROM clientes WHERE cedula = %s", (cedula,)):
            return False, "La cédula ya existe", None
        consulta = "INSERT INTO clientes (cedula, nombre, telefono, email) VALUES (%s, %s, %s, %s)"
        exito, mensaje, ultimo_id = self.ejecutar_consulta(consulta, (cedula, nombre, telefono, email))
        return exito, mensaje, ultimo_id

    def actualizar_cliente(self, id_cliente, cedula, nombre, telefono, email):
        duplicado = self.obtener_todos("SELECT id FROM clientes WHERE cedula = %s AND id != %s", (cedula, id_cliente))
        if duplicado:
            return False, "La cédula ya está en uso por otro cliente"
        if self.existe_telefono(telefono, id_cliente):
            return False, "El número de teléfono ya está en uso por otro cliente"
        consulta = "UPDATE clientes SET cedula=%s, nombre=%s, telefono=%s, email=%s WHERE id=%s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (cedula, nombre, telefono, email, id_cliente))
        return exito, mensaje

    def existe_telefono(self, telefono, id_cliente=None):
        if id_cliente:
            consulta = "SELECT id FROM clientes WHERE telefono = %s AND id != %s"
            parametros = (telefono, id_cliente)
        else:
            consulta = "SELECT id FROM clientes WHERE telefono = %s"
            parametros = (telefono,)
        return bool(self.obtener_todos(consulta, parametros))

    def eliminar_cliente(self, id_cliente):
        consulta = "DELETE FROM clientes WHERE id=%s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (id_cliente,))
        return exito, mensaje

    def obtener_cliente_por_id(self, id_cliente):
        resultado = self.obtener_todos("SELECT id, cedula, nombre, telefono, email FROM clientes WHERE id=%s", (id_cliente,))
        return resultado[0] if resultado else None

    def listar_vehiculos(self):
        consulta = """
            SELECT v.id, v.placa, v.marca, v.modelo, c.nombre as cliente_nombre, v.cliente_id
            FROM vehiculos v
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.id
        """
        return self.obtener_todos(consulta)

    def listar_clientes_combo(self):
        return self.obtener_todos("SELECT id, nombre FROM clientes ORDER BY nombre")
    
    def agregar_vehiculo(self, placa, marca, modelo, cliente_id):
        if self.obtener_todos("SELECT id FROM vehiculos WHERE placa = %s", (placa,)):
            return False, "La placa ya existe", None
        consulta = "INSERT INTO vehiculos (placa, marca, modelo, cliente_id) VALUES (%s, %s, %s, %s)"
        exito, mensaje, ultimo_id = self.ejecutar_consulta(consulta, (placa.upper(), marca, modelo, cliente_id))
        return exito, mensaje, ultimo_id

    def actualizar_vehiculo(self, id_vehiculo, placa, marca, modelo, cliente_id):
        duplicado = self.obtener_todos("SELECT id FROM vehiculos WHERE placa = %s AND id != %s", (placa, id_vehiculo))
        if duplicado:
            return False, "La placa ya está en uso por otro vehículo"
        consulta = "UPDATE vehiculos SET placa=%s, marca=%s, modelo=%s, cliente_id=%s WHERE id=%s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (placa.upper(), marca, modelo, cliente_id, id_vehiculo))
        return exito, mensaje

    def obtener_vehiculo_por_id(self, id_vehiculo):
        resultado = self.obtener_todos("SELECT id, placa, marca, modelo, cliente_id FROM vehiculos WHERE id=%s", (id_vehiculo,))
        return resultado[0] if resultado else None

    def eliminar_vehiculo(self, id_vehiculo):
        consulta = "DELETE FROM vehiculos WHERE id=%s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (id_vehiculo,))
        return exito, mensaje

    def listar_ordenes_completas(self):
        consulta = """
            SELECT orden_id AS id, descripcion, estado, fecha, total_orden_usd,
                   placa, marca, modelo,
                   cliente AS cliente_nombre
            FROM v_ordenes_completas
            ORDER BY fecha DESC
        """
        return self.obtener_todos(consulta)

    def listar_vehiculos_con_cliente(self):
        consulta = """
            SELECT v.id, v.placa, v.marca, v.modelo, c.nombre AS cliente_nombre
            FROM vehiculos v
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.placa
        """
        return self.obtener_todos(consulta)

    def crear_orden(self, vehiculo_id, descripcion, estado="Ingresado", total=0):
        consulta = "INSERT INTO ordenes (vehiculo_id, descripcion, estado, fecha, mano_de_obra) VALUES (%s, %s, %s, NOW(), %s)"
        exito, mensaje, ultimo_id = self.ejecutar_consulta(consulta, (vehiculo_id, descripcion, estado, total))
        return exito, mensaje, ultimo_id

    def obtener_orden_completa(self, id_orden):
        consulta = """
            SELECT 
                o.id, o.descripcion, o.estado, o.fecha,
                v.placa, v.marca, v.modelo,
                c.nombre AS cliente_nombre
            FROM ordenes o
            JOIN vehiculos v ON o.vehiculo_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            WHERE o.id = %s
        """
        resultado = self.obtener_todos(consulta, (id_orden,))
        return resultado[0] if resultado else None

    def actualizar_estado_orden(self, id_orden, nuevo_estado):
        consulta = "UPDATE ordenes SET estado = %s WHERE id = %s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (nuevo_estado, id_orden))
        return exito, mensaje

    def eliminar_orden(self, id_orden):
        consulta = "DELETE FROM ordenes WHERE id=%s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (id_orden,))
        return exito, mensaje

    def listar_repuestos(self):
        return self.obtener_todos("SELECT id, nombre, descripcion, precio, stock, proveedor FROM repuestos ORDER BY nombre")

    def agregar_repuesto(self, nombre, descripcion, precio, stock, proveedor=""):
        consulta = "INSERT INTO repuestos (nombre, descripcion, precio, stock, proveedor) VALUES (%s, %s, %s, %s, %s)"
        exito, mensaje, ultimo_id = self.ejecutar_consulta(consulta, (nombre, descripcion, precio, stock, proveedor))
        return exito, mensaje, ultimo_id

    def actualizar_repuesto(self, id_repuesto, nombre, descripcion, precio, stock, proveedor=""):
        consulta = "UPDATE repuestos SET nombre=%s, descripcion=%s, precio=%s, stock=%s, proveedor=%s WHERE id=%s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (nombre, descripcion, precio, stock, proveedor, id_repuesto))
        return exito, mensaje

    def eliminar_repuesto(self, id_repuesto):
        consulta = "DELETE FROM repuestos WHERE id=%s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (id_repuesto,))
        return exito, mensaje

    def obtener_repuesto_por_id(self, id_repuesto):
        resultado = self.obtener_todos("SELECT id, nombre, descripcion, precio, stock, proveedor FROM repuestos WHERE id=%s", (id_repuesto,))
        return resultado[0] if resultado else None

    def actualizar_stock(self, id_repuesto, cantidad):
        consulta = "UPDATE repuestos SET stock = stock - %s WHERE id = %s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (cantidad, id_repuesto))
        return exito, mensaje

    def incrementar_stock(self, id_repuesto, cantidad):
        consulta = "UPDATE repuestos SET stock = stock + %s WHERE id = %s"
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (cantidad, id_repuesto))
        return exito, mensaje

    def ingresar_stock(self, id_repuesto, cantidad, motivo, usuario_id, usuario_nombre):
        """Suma unidades al inventario y deja registrada la entrada.

        Igual que descontar_stock: el cambio de stock y el movimiento van en la misma
        transaccion, asi el inventario nunca queda modificado sin su registro.
        """
        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0."

        conexion = self.obtener_conexion()
        if not conexion:
            return False, "Error de conexión"

        cursor = conexion.cursor()
        try:
            cursor.execute("UPDATE repuestos SET stock = stock + %s WHERE id = %s",
                           (cantidad, id_repuesto))
            if cursor.rowcount == 0:
                conexion.rollback()
                return False, "No se encontró el repuesto."

            cursor.execute(
                """
                    INSERT INTO movimientos_inventario
                        (repuesto_id, tipo, cantidad, motivo, usuario_id, usuario_nombre)
                    VALUES (%s, 'ENTRADA', %s, %s, %s, %s)
                """,
                (id_repuesto, cantidad, motivo, usuario_id, usuario_nombre)
            )
            conexion.commit()
            return True, "Entrada registrada"
        except Error as e:
            conexion.rollback()
            return False, f"Error: {e}"
        finally:
            cursor.close()
            conexion.close()

    def registrar_movimiento(self, repuesto_id, tipo, cantidad, motivo, usuario_id, usuario_nombre):
        consulta = """
            INSERT INTO movimientos_inventario (repuesto_id, tipo, cantidad, motivo, usuario_id, usuario_nombre)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        exito, mensaje, _ = self.ejecutar_consulta(
            consulta, (repuesto_id, tipo, cantidad, motivo, usuario_id, usuario_nombre)
        )
        return exito, mensaje

    def descontar_stock(self, id_repuesto, cantidad, motivo, usuario_id, usuario_nombre):
        """Descuenta unidades del inventario y deja registrada la salida.

        El descuento y el movimiento se guardan en la misma transaccion, para que nunca
        quede stock modificado sin su registro. El "stock >= cantidad" dentro del UPDATE
        impide que el inventario quede en negativo.
        """
        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0."

        conexion = self.obtener_conexion()
        if not conexion:
            return False, "Error de conexión"

        cursor = conexion.cursor()
        try:
            cursor.execute(
                "UPDATE repuestos SET stock = stock - %s WHERE id = %s AND stock >= %s",
                (cantidad, id_repuesto, cantidad)
            )
            if cursor.rowcount == 0:
                conexion.rollback()
                cursor.execute("SELECT stock FROM repuestos WHERE id = %s", (id_repuesto,))
                fila = cursor.fetchone()
                if not fila:
                    return False, "No se encontró el repuesto."
                disponibles = int(fila[0])
                if cantidad > disponibles:
                    return False, (f"No hay stock suficiente. Solo quedan "
                                   f"{disponibles} unidades disponibles.")
                return False, "No se pudo descontar el stock."

            cursor.execute(
                """
                    INSERT INTO movimientos_inventario
                        (repuesto_id, tipo, cantidad, motivo, usuario_id, usuario_nombre)
                    VALUES (%s, 'SALIDA', %s, %s, %s, %s)
                """,
                (id_repuesto, cantidad, motivo, usuario_id, usuario_nombre)
            )
            conexion.commit()
            return True, "Salida registrada"
        except Error as e:
            conexion.rollback()
            return False, f"Error: {e}"
        finally:
            cursor.close()
            conexion.close()

    def listar_movimientos(self, limite=200):
        consulta = """
            SELECT m.id, r.nombre AS repuesto, m.tipo, m.cantidad, m.motivo,
                   m.usuario_nombre, m.fecha_hora
            FROM movimientos_inventario m
            JOIN repuestos r ON m.repuesto_id = r.id
            ORDER BY m.fecha_hora DESC
            LIMIT %s
        """
        return self.obtener_todos(consulta, (limite,))

    def registrar_log(self, usuario_id, usuario_nombre, tabla, registro_id, accion, descripcion=""):
        consulta = """
            INSERT INTO logs_auditoria (usuario_id, usuario_nombre, tabla_afectada, registro_id, accion, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        exito, mensaje, _ = self.ejecutar_consulta(consulta, (usuario_id, usuario_nombre, tabla, registro_id, accion, descripcion))
        return exito, mensaje

    def listar_logs(self, limite=100):
        consulta = """
            SELECT id, usuario_nombre, tabla_afectada, registro_id, accion, descripcion, fecha_hora
            FROM logs_auditoria
            ORDER BY fecha_hora DESC
            LIMIT %s
        """
        return self.obtener_todos(consulta, (limite,))

    def listar_logs_por_tabla(self, tabla):
        consulta = """
            SELECT id, usuario_nombre, tabla_afectada, registro_id, accion, descripcion, fecha_hora
            FROM logs_auditoria
            WHERE tabla_afectada = %s
            ORDER BY fecha_hora DESC
        """
        return self.obtener_todos(consulta, (tabla,))

    def contar_logs_por_accion(self):
        consulta = """
            SELECT accion, COUNT(*) as total
            FROM logs_auditoria
            GROUP BY accion
        """
        return self.obtener_todos(consulta)

    def obtener_estadisticas_taller(self):
        estadisticas = {}
        clientes = self.obtener_todos("SELECT COUNT(*) as total FROM clientes")
        estadisticas['total_clientes'] = clientes[0]['total'] if clientes else 0
        vehiculos = self.obtener_todos("SELECT COUNT(*) as total FROM vehiculos")
        estadisticas['total_vehiculos'] = vehiculos[0]['total'] if vehiculos else 0
        ordenes_estado = self.obtener_todos("""
            SELECT estado, COUNT(*) as total 
            FROM ordenes 
            GROUP BY estado
        """)
        estadisticas['ordenes_por_estado'] = ordenes_estado or []
        ordenes_mes = self.obtener_todos("""
            SELECT COUNT(*) as total 
            FROM ordenes 
            WHERE MONTH(fecha) = MONTH(CURRENT_DATE()) 
            AND YEAR(fecha) = YEAR(CURRENT_DATE())
        """)
        estadisticas['ordenes_mes'] = ordenes_mes[0]['total'] if ordenes_mes else 0
        repuestos_bajo_stock = self.obtener_todos("""
            SELECT COUNT(*) as total 
            FROM repuestos 
            WHERE stock < %s
        """, (BAJO_STOCK,))
        estadisticas['repuestos_bajo_stock'] = repuestos_bajo_stock[0]['total'] if repuestos_bajo_stock else 0
        return estadisticas

    def obtener_id_usuario(self, nombre_usuario):
        resultado = self.obtener_todos("SELECT id FROM usuarios WHERE username = %s", (nombre_usuario,))
        return resultado[0]['id'] if resultado else None

    def obtener_detalle_orden_pagos(self, id_orden):
        consulta = """
            SELECT 
                orden_id AS id, 
                descripcion, 
                estado, 
                COALESCE(total_orden_usd, 0) AS total_orden_usd,
                COALESCE(total_pagado, 0) AS total_pagado,
                cliente AS cliente_nombre,
                CONCAT(marca, ' ', modelo, ' (', placa, ')') AS vehiculo
            FROM v_ordenes_completas
            WHERE orden_id = %s
        """
        resultado = self.obtener_todos(consulta, (id_orden,))
        if resultado:
            return resultado[0]
        # Si no encuentra la orden, devolver un diccionario con valores por defecto
        return {
            'id': id_orden,
            'descripcion': 'Orden no encontrada',
            'estado': 'Desconocido',
            'total_orden_usd': 0,
            'total_pagado': 0,
            'cliente_nombre': 'N/A',
            'vehiculo': 'N/A'
        }

    def listar_cuentas_por_cobrar(self):
        """Todas las ordenes con su total, lo pagado y el saldo pendiente."""
        consulta = """
            SELECT orden_id AS id,
                   cliente,
                   CONCAT(marca, ' ', modelo) AS vehiculo,
                   COALESCE(total_orden_usd, 0) AS total_orden_usd,
                   COALESCE(total_pagado, 0) AS pagado,
                   COALESCE(saldo, 0) AS saldo
            FROM v_ordenes_completas
            ORDER BY orden_id DESC
        """
        return self.obtener_todos(consulta)

    def obtener_totales_recaudados(self):
        """Total cobrado historico y total del mes en curso, en USD."""
        consulta = """
            SELECT 
                COALESCE(SUM(monto_ref_usd), 0) AS total,
                COALESCE(SUM(
                    CASE WHEN YEAR(fecha_pago) = YEAR(CURDATE()) 
                          AND MONTH(fecha_pago) = MONTH(CURDATE()) 
                         THEN monto_ref_usd ELSE 0 END
                ), 0) AS mes
            FROM pagos
        """
        resultado = self.obtener_todos(consulta)
        if resultado:
            return resultado[0]
        return {'total': 0, 'mes': 0}

    def listar_meses_con_pagos(self):
        """Meses en los que se registraron pagos, del mas reciente al mas antiguo."""
        consulta = """
            SELECT DISTINCT YEAR(fecha_pago) AS anio, MONTH(fecha_pago) AS mes
            FROM pagos
            ORDER BY anio DESC, mes DESC
        """
        return self.obtener_todos(consulta) or []

    def obtener_recaudos_del_mes(self, anio, mes):
        """Detalle por orden de lo cobrado en un mes, con el saldo pendiente de cada una."""
        consulta = """
            SELECT oc.orden_id AS orden_id,
                   oc.cliente,
                   oc.placa,
                   oc.total_orden_usd,
                   SUM(p.monto_ref_usd) AS cobrado_mes,
                   COALESCE(oc.total_pagado, 0) AS cobrado_total
            FROM v_ordenes_completas oc
            JOIN pagos p ON p.orden_id = oc.orden_id
            WHERE YEAR(p.fecha_pago) = %s AND MONTH(p.fecha_pago) = %s
            GROUP BY oc.orden_id, oc.cliente, oc.placa, oc.total_orden_usd, oc.total_pagado
            ORDER BY oc.orden_id
        """
        return self.obtener_todos(consulta, (anio, mes)) or []

    def listar_pagos_por_orden(self, id_orden):
        consulta = """
            SELECT id, monto_original, moneda, tasa_cambio, monto_ref_usd,
                   fecha_pago, metodo_pago, referencia
            FROM pagos
            WHERE orden_id = %s
            ORDER BY fecha_pago DESC
        """
        return self.obtener_todos(consulta, (id_orden,))

    def registrar_pago(self, orden_id, monto_original, moneda, tasa_cambio, monto_ref_usd, metodo_pago, referencia=""):
        consulta = """
            INSERT INTO pagos (orden_id, monto_original, moneda, tasa_cambio, monto_ref_usd, metodo_pago, referencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.ejecutar_consulta(consulta, (orden_id, monto_original, moneda, tasa_cambio, monto_ref_usd, metodo_pago, referencia))

    def obtener_resumen_pagos(self):
        consulta = """
            SELECT 
                DATE_FORMAT(fecha_pago, '%Y-%m') as mes,
                SUM(monto_ref_usd) as total_usd
            FROM pagos
            GROUP BY mes
            ORDER BY mes
        """
        return self.obtener_todos(consulta)

    def obtener_distribucion_monedas(self):
        consulta = """
            SELECT moneda, SUM(monto_ref_usd) as total_usd
            FROM pagos
            GROUP BY moneda
        """
        return self.obtener_todos(consulta)

    def obtener_historial_pagos(self):
        consulta = """
            SELECT p.id, o.id as orden_id, c.nombre as cliente,
                CONCAT(v.marca, ' ', v.modelo) as vehiculo,
                p.monto_original, p.moneda, p.tasa_cambio,
                p.monto_ref_usd, p.fecha_pago, p.metodo_pago, p.referencia
            FROM pagos p
            JOIN ordenes o ON p.orden_id = o.id
            JOIN vehiculos v ON o.vehiculo_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY p.fecha_pago DESC
        """
        return self.obtener_todos(consulta)