# Manual de Usuario y Sistema — Taller Don Julio

**Sistema de Gestión Operativa para Taller Mecánico**  
**Versión:** 1.0  
**Fecha:** Septiembre 2026  
**Tecnologías:** Python (CustomTkinter, ReportLab) & MySQL  

---

## ÍNDICE DE CONTENIDOS
1. [Introducción y Objetivos](#1-introducción-y-objetivos)
2. [Arquitectura y Requisitos del Sistema](#2-arquitectura-y-requisitos-del-sistema)
3. [Instalación y Configuración Inicial](#3-instalación-y-configuración-inicial)
4. [Manual de Usuario (Guía Operativa)](#4-manual-de-usuario-guía-operativa)
   - 4.1 [Inicio de Sesión y Roles](#41-inicio-de-sesión-y-roles)
   - 4.2 [Módulo de Clientes](#42-módulo-de-clientes)
   - 4.3 [Módulo de Vehículos](#43-módulo-de-vehículos)
   - 4.4 [Módulo de Órdenes de Servicio](#44-módulo-de-órdenes-de-servicio)
   - 4.5 [Módulo de Repuestos e Inventario](#45-módulo-de-repuestos-e-inventario)
   - 4.6 [Módulo de Reportes y PDF](#46-módulo-de-reportes-y-pdf)
5. [Manual de Administración y Mantenimiento](#5-manual-de-administración-y-mantenimiento)
   - 5.1 [Gestión de Usuarios y Permisos (RBAC)](#51-gestión-de-usuarios-y-permisos-rbac)
   - 5.2 [Respaldos y Restauración de Base de Datos](#52-respaldos-y-restauración-de-base-de-datos)
   - 5.3 [Sistema de Auditoría y Logs](#53-sistema-de-auditoría-y-logs)
6. [Resolución de Problemas Frecuentes (FAQ)](#6-resolución-de-problemas-frecuentes-faq)

---

## 1. INTRODUCCIÓN Y OBJETIVOS

El **Sistema de Gestión Operativa Taller Don Julio** es una solución de software de escritorio desarrollada en Python con interfaz gráfica moderna (**CustomTkinter**) y persistencia de datos relacional en **MySQL**.

### Objetivos Principales:
* Centralizar el registro de clientes, vehículos y la trazabilidad de reparaciones.
* Controlar el inventario de repuestos y asignación de personal mecánico.
* Garantizar la seguridad mediante el control de acceso basado en roles (**RBAC**).
* Mantener la integridad de datos a través de registros de auditoría y copias de seguridad respaldadas.

---

## 2. ARQUITECTURA Y REQUISITOS DEL SISTEMA

### Requisitos de Hardware Mínimos:
* **Procesador:** Dual Core 2.0 GHz o superior.
* **Memoria RAM:** 2 GB mínimo (4 GB recomendado).
* **Almacenamiento:** 500 MB de espacio disponible.

### Requisitos de Software:
* **Sistema Operativo:** Linux (Ubuntu, Debian, Linux Mint, etc.) o Windows 10/11.
* **Lenguaje:** Python 3.10 o superior.
* **Base de Datos:** MySQL Server 8.0 o MariaDB 10.5+.
* **Herramientas de CLI:** `mysqldump` instalado en el PATH del sistema para copias de seguridad.

### Dependencias de Python (`requirements.txt`):
* `customtkinter`
* `pillow`
* `mysql-connector-python`
* `reportlab`

---

## 3. INSTALACIÓN Y CONFIGURACIÓN INICIAL

### Paso 1: Clonar / Copiar el Código Fuente
Coloque la carpeta del proyecto en su directorio local de trabajo.

### Paso 2: Instalación de Dependencias
Ejecute en la terminal:
```bash
pip install customtkinter pillow mysql-connector-python reportlab
```

### Paso 3: Despliegue de la Base de Datos
Importe la estructura y los datos iniciales ejecutando el archivo `basededatos.sql`:
```bash
mysql -u root -p < basededatos.sql
```

Esto creará la base de datos `taller`, las tablas principales (`usuarios`, `clientes`, `vehiculos`, `ordenes`, `repuestos`, `personal`, `detalle_mano_obra`, `logs_auditoria`), las vistas y los usuarios por defecto.

---

## 4. MANUAL DE USUARIO (GUÍA OPERATIVA)

### 4.1 Inicio de Sesión y Roles

1. Ejecute la aplicación iniciando `python main.py` (o mediante el módulo de interfaz correspondiente).
2. Ingrese su **Nombre de Usuario** y **Contraseña**.

#### Roles de Usuario y Accesos:
* **Administrador (`admin`):** Acceso total a todos los módulos, reportes, gestión de usuarios y backups.
* **Secretaria (`secretaria`):** Gestión de clientes, vehículos, registro e ingreso de órdenes de servicio y consulta de repuestos.
* **Mecánico (`mecanico`):** Consulta y actualización del estado de órdenes asignadas, agregar repuestos y detalle de mano de obra.
* **Auditor (`auditor`):** Modo lectura exclusiva para revisiones e inspección de tablas y logs de auditoría.

---

### 4.2 Módulo de Clientes

Permite registrar, editar y consultar los datos de los propietarios de los vehículos.

* **Registrar Cliente:**
  1. Diríjase a la pestaña **Clientes**.
  2. Complete los campos:
     - **Cédula:** Formato flexible (6 a 8 dígitos numéricos).
     - **Nombre Completo:** Obligatorio.
     - **Teléfono:** (Opcional) 11 dígitos.
     - **Correo Electrónico:** (Opcional) Debe cumplir formato válido.
  3. Presione el botón **Guardar**.
* **Editar / Eliminar:** Seleccione un registro de la tabla para cargar sus datos en el formulario y ejecutar la actualización o borrado.

---

### 4.3 Módulo de Vehículos

Maneja el parque automotor registrado en el taller.

* **Asociación de Vehículo:**
  1. Ingrese la **Placa** (Identificador único).
  2. Ingrese **Marca** y **Modelo**.
  3. Seleccione el **Cliente Propietario** desde el menú desplegable.
  4. Presione **Guardar Vehículo**.

---

### 4.4 Módulo de Órdenes de Servicio

Es el módulo central del taller para la recepción, seguimiento y entrega de automóviles.

* **Apertura de Orden:**
  1. Seleccione el vehículo por su placa.
  2. Escriba la descripción detallada de la falla o trabajo a realizar.
  3. El estado inicial se asignará automáticamente como **"Ingresado"**.
* **Gestión de la Reparación:**
  - **Asignación de Repuestos:** Permite vincular repuestos consumidos, descontándolos del inventario general.
  - **Mano de Obra:** Permite registrar las horas de trabajo ejecutadas por el personal mecánico.
  - **Actualización de Estado:** Cambie el estado conforme avance el trabajo (*Ingresado* $
ightarrow$ *En Proceso* $
ightarrow$ *Completado* $
ightarrow$ *Entregado*).

---

### 4.5 Módulo de Repuestos e Inventario

Control de catálogo de repuestos y repuestos consumidos.

* **Agregar Repuesto:**
  - Registre el **Nombre**, **Descripción**, **Precio Unitario**, **Stock Inicial** y **Proveedor**.
* **Alertas de Inventario:**
  - El sistema resaltará los repuestos cuya cantidad en stock esté por debajo del límite mínimo.

---

### 4.6 Módulo de Reportes y PDF

Permite la generación de archivos PDF para impresión o archivo físico utilizando la librería `ReportLab`.

* **Ficha de Orden de Servicio:** Genera un comprobante formateado para entregar al cliente al momento de recibir el vehículo.
* **Reporte de Facturación / Cierre:** Resumen con el desglose de repuestos consumidos, costo de mano de obra e importe total.

---

## 5. MANUAL DE ADMINISTRACIÓN Y MANTENIMIENTO

### 5.1 Gestión de Usuarios y Permisos (RBAC)

Desde el módulo **Configuración** (exclusivo para el rol `admin`):
* **Crear Usuario:** Permite crear nuevos usuarios definiendo su clave cifrada (`SHA256`) y asignándoles un rol (`admin`, `secretaria`, `mecanico`, `auditor`).
* **Regla de Seguridad:** El sistema cuenta con protección contra auto-eliminación, impidiendo que el administrador en sesión borre su propia cuenta activa.

---

### 5.2 Respaldos y Restauración de Base de Datos

* **Exportar Backup (.sql):**
  1. Ingrese a **Configuración** $
ightarrow$ **Pestaña Respaldos**.
  2. Haga clic en **Exportar Base de Datos**.
  3. El sistema ejecutará el volcado nativo utilizando `mysqldump` de forma segura mediante la variable de entorno `MYSQL_PWD`, almacenando el archivo con la estampa de tiempo en el nombre (`backup_taller_YYYYMMDD_HHMMSS.sql`).
* **Restauración:**
  Para restaurar un respaldo exportado previo, ejecute en la consola del servidor:
  ```bash
  mysql -u root -p taller < ruta/del/archivo_backup.sql
  ```

---

### 5.3 Sistema de Auditoría y Logs

El sistema implementa una tabla de trazabilidad (`logs_auditoria`) que registra automáticamente:
* **Usuario:** Nombre de usuario que ejecutó la acción.
* **Tabla Afectada:** Nombre de la tabla (`clientes`, `vehiculos`, `ordenes`, etc.).
* **ID de Registro:** Identificador único (`lastrowid`) del registro insertado, modificado o eliminado.
* **Acción:** Tipo de operación (`INSERT`, `UPDATE`, `DELETE`).
* **Fecha y Hora:** Timestamp exacto del suceso.

---

## 6. RESOLUCIÓN DE PROBLEMAS FRECUENTES (FAQ)

### 1. Error: "No se encuentra el cliente MySQL (mysqldump)"
* **Causa:** El ejecutable `mysqldump` no está configurado en las variables de entorno (`PATH`) del sistema operativo.
* **Solución:** Instale el paquete `mysql-client` en Linux (`sudo apt install mysql-client`) o agregue la ruta binaria de MySQL en Windows.

### 2. Error de Clave Duplicada al Registrar Teléfono
* **Causa:** Intentar guardar una cadena vacía en una columna con restricción `UNIQUE`.
* **Solución:** Si el cliente no posee teléfono, deje el campo completamente vacío para que el sistema envíe un valor `NULL` a la base de datos.

### 3. La contraseña de acceso no funciona tras ser cambiada en MySQL
* **Causa:** Las contraseñas en la tabla `usuarios` deben guardarse aplicando la función de hash `SHA2(password, 256)`.
* **Solución:** Al actualizar claves directamente en la base de datos, asegúrese de usar:
  ```sql
  UPDATE usuarios SET password = SHA2('nueva_clave', 256) WHERE username = 'usuario';
  ```

---
*Manual redactado y estructurado para el proyecto **Taller Don Julio**.*
