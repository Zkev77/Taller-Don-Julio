CREATE DATABASE taller;
USE taller;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR,
    password BLOB
);

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    placa VARCHAR(20)
);

CREATE TABLE ordenes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT,
    descripcion TEXT,
    estado VARCHAR(50),
    fecha DATETIME
);
