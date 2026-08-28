CREATE DATABASE taller;
USE taller;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'mecanico') NOT NULL DEFAULT 'mecanico'
);

INSERT INTO usuarios (username, password, rol) 
VALUES ('admin', SHA2('admin123', 256), 'admin');

INSERT INTO usuarios (username, password, rol) 
VALUES ('mecanico', SHA2('mecanico123', 256), 'mecanico');



CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(8) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(11),
    UNIQUE (telefono),
    email VARCHAR(100)
);

CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    placa VARCHAR(10) NOT NULL UNIQUE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE ordenes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT NOT NULL,
    descripcion TEXT,
    estado VARCHAR(50) DEFAULT 'Ingresado',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS repuestos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    proveedor VARCHAR(100)
);


CREATE VIEW vista_ordenes_completas AS
SELECT 
    o.id AS orden_id,
    c.nombre AS cliente,
    v.placa,
    v.marca,
    v.modelo,
    o.descripcion,
    o.estado,
    o.fecha
FROM ordenes o
JOIN vehiculos v ON o.vehiculo_id = v.id
JOIN clientes c ON v.cliente_id = c.id;

ALTER TABLE clientes MODIFY cedula VARCHAR(11) NOT NULL UNIQUE;

CREATE TABLE IF NOT EXISTS orden_repuestos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    orden_id INT NOT NULL,
    repuesto_id INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) ON DELETE CASCADE,
    FOREIGN KEY (repuesto_id) REFERENCES repuestos(id)
);

CREATE TABLE IF NOT EXISTS personal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    fecha_contrato DATE,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS detalle_mano_obra (
    id INT AUTO_INCREMENT PRIMARY KEY,
    orden_id INT NOT NULL,
    personal_id INT NOT NULL,
    descripcion TEXT NOT NULL,
    horas DECIMAL(5,2) DEFAULT 0,
    costo_por_hora DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) DEFAULT 0,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) ON DELETE CASCADE,
    FOREIGN KEY (personal_id) REFERENCES personal(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS logs_auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    usuario_nombre VARCHAR(50),
    tabla_afectada VARCHAR(50) NOT NULL,
    registro_id INT NOT NULL,
    accion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    descripcion TEXT,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

ALTER TABLE usuarios MODIFY rol ENUM('admin', 'mecanico', 'auditor', 'secretaria') NOT NULL DEFAULT 'mecanico';

INSERT IGNORE INTO usuarios (username, password, rol) VALUES
('Julio', SHA2('admin123', 256), 'admin'),
('Dayary', SHA2('secretaria123', 256), 'secretaria'),
('Mecanico1', SHA2('mecanico123', 256), 'mecanico'),
('Auditor1', SHA2('auditor123', 256), 'auditor');

ALTER TABLE ordenes ADD COLUMN total_orden_usd DECIMAL(10,2) DEFAULT 0;

CREATE TABLE IF NOT EXISTS pagos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    orden_id INT NOT NULL,
    monto_original DECIMAL(12,2) NOT NULL,
    moneda ENUM('USD', 'COP', 'BS') NOT NULL,
    tasa_cambio DECIMAL(10,2) NOT NULL,
    monto_ref_usd DECIMAL(10,2) NOT NULL,
    fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
    metodo_pago ENUM('Efectivo', 'Transferencia', 'Pago Movil', 'Zelle', 'Otro') NOT NULL,
    referencia VARCHAR(50),
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) ON DELETE CASCADE
);
 