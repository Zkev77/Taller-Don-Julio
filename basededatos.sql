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

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    placa VARCHAR(20) NOT NULL UNIQUE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE ordenes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT NOT NULL,
    descripcion TEXT,
    estado VARCHAR(50) DEFAULT 'Pendiente',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id) ON DELETE CASCADE
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

INSERT INTO clientes (cedula, nombre, telefono, email) VALUES
('V12345678', 'Juan Pérez', '0412-1234567', 'juan@example.com'),
('V87654321', 'María Gómez', '0416-7654321', 'maria@example.com');

INSERT INTO vehiculos (cliente_id, marca, modelo, placa) VALUES
(1, 'Toyota', 'Corolla', 'ABC123'),
(2, 'Ford', 'Fiesta', 'XYZ789');

INSERT INTO ordenes (vehiculo_id, descripcion, estado) VALUES
(1, 'Cambio de aceite y filtro', 'Completado'),
(2, 'Revisión de frenos', 'En proceso');