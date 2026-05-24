CREATE DATABASE IF NOT EXISTS taller;
USE taller;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(20) NOT NULL UNIQUE,  -- ¡Añadida la cédula obligatoria!
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    placa VARCHAR(20) NOT NULL UNIQUE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE -- Relación técnica para UPT
);

CREATE TABLE ordenes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT,
    descripcion TEXT,
    estado VARCHAR(50),
    fecha DATETIME,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
);
