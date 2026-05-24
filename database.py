import mysql.connector

def insertar_cliente(cedula, nombre, telefono, email, marca, modelo, placa):
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="developer",
            password="Taller2026",  
            database="taller"
        )
        cursor = conexion.cursor()

        query_buscar_cedula = "SELECT id FROM clientes WHERE cedula = %s"
        cursor.execute(query_buscar_cedula, (cedula,))
        if cursor.fetchone():
            return False, "Error: La cédula ya está registrada con otro cliente."

        query_buscar_placa = "SELECT id FROM vehiculos WHERE placa = %s"
        cursor.execute(query_buscar_placa, (placa,))
        if cursor.fetchone():
            return False, "Error: Esta placa de vehículo ya está registrada."

        query_cliente = "INSERT INTO clientes (cedula, nombre, telefono, email) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_cliente, (cedula, nombre, telefono, email))
        
        cliente_id = cursor.lastrowid

        query_vehiculo = "INSERT INTO vehiculos (cliente_id, marca, modelo, placa) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_vehiculo, (cliente_id, marca, modelo, placa))

        conexion.commit()
        return True, "¡Ingreso completo de Cliente y Vehículo registrado con éxito!"

    except mysql.connector.Error as error:
        return False, f"Error en la base de datos: {error}"

    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()