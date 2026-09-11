# Sistema de Gestión Operativa - Taller Mecánico "Don Julio"

**Versión:** 1.0
**Fecha:** Septiembre 2026
**Tecnologías:** Python (CustomTkinter, ReportLab, Matplotlib) & MySQL

---

## Descripción del Proyecto

El Sistema de Gestión Operativa del Taller Mecánico "Don Julio" es una aplicación de escritorio desarrollada en Python que permite administrar de forma integral los procesos administrativos y técnicos de un taller mecánico. El sistema centraliza el registro de clientes, vehículos, órdenes de servicio, repuestos, pagos en múltiples monedas y la generación de reportes financieros y de auditoría.

Este proyecto fue desarrollado como parte del Proyecto Sociotecnológico II del Programa Nacional de Formación en Informática (PNFI), en la Universidad Politécnica Territorial Agroindustrial del Estado Táchira (UPTAIET).

---

## Características Principales

- Autenticación con control de acceso basado en roles (Administrador, Secretaria, Mecánico y Auditor).
- Gestión completa de clientes con validación de cédula, nombre y teléfono.
- Gestión de vehículos con exportación de listado a PDF.
- Creación y seguimiento de órdenes de servicio con cambio de estado.
- Registro de pagos en múltiples monedas (USD, COP y BS) con tasa de cambio editable.
- Módulo de presupuestos con cuentas por cobrar, historial de pagos y gráficas financieras.
- Gestión de inventario de repuestos con control de stock.
- Auditoría automática de todas las operaciones (INSERT, UPDATE, DELETE) con trazabilidad por usuario.
- Exportación de respaldos de la base de datos en formato .sql.
- Interfaz gráfica moderna y adaptable desarrollada con CustomTkinter.

---

## Requisitos del Sistema

### Hardware

- Procesador: Dual Core 2.0 GHz o superior.
- Memoria RAM: 2 GB mínimo (4 GB recomendado).


### Software

- Sistema Operativo: Windows 10/11 o Linux.
- Python: 3.12 o superior.
- Base de Datos: MySQL Server 8.0.
- Herramienta mysqldump instalada en el PATH (para respaldos).

### Dependencias de Python

El proyecto requiere las siguientes librerías:

```
customtkinter
pillow
mysql-connector-python
reportlab
matplotlib
python-dotenv
pytablericons
```

---

## Instalación y Configuración

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/taller-don-julio.git
cd taller-don-julio
```

### Paso 2: Crear un entorno virtual (opcional pero recomendado)

```bash
python -m venv .venv
source .venv/bin/activate    # En Linux/Mac
# .venv\Scripts\activate     # En Windows
```

### Paso 3: Instalar las dependencias

```bash
pip install customtkinter pillow mysql-connector-python reportlab matplotlib python-dotenv pytablericons
```

### Paso 4: Configurar la base de datos

Importe el script SQL para crear la base de datos y las tablas:

```bash
mysql -u root -p < basededatos.sql
```

Esto creará la base de datos `taller` con las siguientes tablas:

- `usuarios`: credenciales y roles del personal.
- `clientes`: información de los propietarios.
- `vehiculos`: vehículos asociados a clientes.
- `ordenes`: órdenes de servicio con total en USD.
- `repuestos`: inventario de repuestos.
- `orden_repuestos`: relación entre órdenes y repuestos utilizados.
- `pagos`: registro de pagos en múltiples monedas.
- `logs_auditoria`: trazabilidad de todas las operaciones.

### Paso 5: Crear el archivo .env

Cree un archivo llamado `.env` en la raíz del proyecto con las siguientes variables:

```env
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=taller
```

Si no tiene un usuario específico, puede crear uno en MySQL:

```sql
CREATE USER 'tu_usuario'@'localhost' IDENTIFIED BY 'tu_contraseña';
GRANT ALL PRIVILEGES ON taller.* TO 'tu_usuario'@'localhost';
FLUSH PRIVILEGES;
```

### Paso 6: Ejecutar la aplicación

```bash
python login.py
```

---

## Roles y Permisos

El sistema implementa un esquema de control de acceso basado en roles (RBAC). Cada usuario visualiza únicamente los módulos autorizados según su rol.

| Módulo | Administrador | Secretaria | Mecánico | Auditor |
|--------|---------------|------------|----------|---------|
| Inicio | Sí | Sí | Sí | Sí |
| Clientes | Sí | Sí | No | Solo lectura |
| Vehículos | Sí | Sí | Solo lectura | Solo lectura |
| Servicios y Reparaciones | Sí | Sí | Cambio de estado | Solo lectura |
| Presupuestos | Sí | Sí | No | Solo lectura |
| Repuestos | Sí | Sí | No | Solo lectura |
| Reportes y Auditoría | Sí | No | No | Sí |
| Configuración | No | No | No | Sí |

### Credenciales iniciales

Las siguientes credenciales son provisionadas durante la instalación inicial y deben modificarse en el primer uso:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| Julio | admin123 | Administrador |
| Dayary | secretaria123 | Secretaria |
| Mecanico1 | mecanico123 | Mecánico |
| Auditor1 | auditor123 | Auditor |

---

## Módulos del Sistema

### Inicio (Panel de Control)

Muestra un mensaje de bienvenida con el nombre del usuario y su rol, además de un resumen con el total de clientes y vehículos registrados.

### Clientes

Permite registrar, consultar, editar y eliminar clientes. Valida que la cédula y el teléfono sean únicos.

### Vehículos

Permite registrar, consultar, editar y eliminar vehículos asociados a clientes. Incluye exportación del listado a PDF.

### Servicios y Reparaciones

Módulo central del sistema. Permite crear órdenes, describir fallas, asignar total en USD, cambiar el estado (Ingresado, Revisión, Trabajando, Completado, Entregado) y registrar pagos en múltiples monedas.

### Presupuestos

Panel de control financiero. Muestra cuentas por cobrar, historial de pagos y gráficas de ingresos mensuales y distribución por moneda.

### Repuestos

Permite gestionar el inventario de repuestos del taller con control de stock.

### Reportes y Auditoría

Muestra estadísticas generales del taller y permite consultar los logs de auditoría con trazabilidad de todas las operaciones realizadas.

### Configuración (solo Auditor)

Permite gestionar usuarios del sistema, cambiar contraseñas y exportar respaldos de la base de datos.

---

## Sistema de Auditoría

El sistema registra automáticamente en la tabla `logs_auditoria` cada operación de inserción, modificación o eliminación realizada en la aplicación, incluyendo:

- Usuario que ejecutó la acción.
- Tabla afectada.
- Identificador del registro.
- Tipo de acción (INSERT, UPDATE, DELETE).
- Descripción de la operación.
- Fecha y hora exacta.

---

## Respaldos de la Base de Datos

Desde el módulo de Configuración (rol Auditor), se puede exportar un respaldo completo de la base de datos en formato .sql. El sistema utiliza la variable de entorno `MYSQL_PWD` para proteger la contraseña durante el proceso.

Para restaurar un respaldo:

```bash
mysql -u root -p taller < ruta/del/archivo_backup.sql
```

---

## Solución de Problemas Frecuentes

### 1. Error: "No se encuentra el comando mysqldump"

Causa: El ejecutable `mysqldump` no está en el PATH del sistema.
Solución: En Linux, instale `mysql-client` (`sudo apt install mysql-client`). En Windows, agregue la ruta binaria de MySQL a las variables de entorno.

### 2. Error al iniciar sesión

Causa: Credenciales incorrectas o usuario no registrado.
Solución: Verifique el usuario y la contraseña. Si el problema persiste, consulte al Auditor para restablecer su cuenta.

### 3. El sistema indica que la cédula o el teléfono ya están registrados

Causa: Los campos de cédula y teléfono tienen restricción de unicidad.
Solución: Verifique que los datos ingresados no correspondan a un cliente ya existente.

### 4. Error al registrar un pago

Causa: El monto en dólares supera el saldo pendiente de la orden.
Solución: Verifique la tasa de cambio y el monto en la moneda seleccionada.

### 5. La contraseña de acceso no funciona tras ser cambiada directamente en MySQL

Causa: Las contraseñas deben almacenarse aplicando hash SHA-256.
Solución: Al actualizar claves directamente en la base de datos, use:

```sql
UPDATE usuarios SET password = SHA2('nueva_clave', 256) WHERE username = 'usuario';
```

---

## Estructura del Proyecto

```
taller-don-julio/
├── .env
├── basededatos.sql
├── login.py
├── interfaz.py
├── clientes.py
├── vehiculos.py
├── servicios.py
├── repuestos.py
├── presupuesto.py
├── reportes.py
├── configuracion.py
├── database.py
├── colores_app.py
└── README.md
```

---

## Autores

- David Abraham Ragua Ramírez (C.I. 32.720.823)
- Kevin David Martínez Velazco (C.I. 32.326.035)
- Dayary Amiray Sepulveda Nuncira (C.I. 31.859.457)

Institución: Universidad Politécnica Territorial Agroindustrial del Estado Táchira (UPTAIET)
Programa: PNF en Informática
Proyecto: Sociotecnológico II

---
