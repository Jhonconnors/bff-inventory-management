-- Esquema PostgreSQL para la inicialización de una base de datos local.
-- Proyecto: Plataforma Web de Gestión de Activos Tecnológicos


-- 1. Tablas de Seguridad y Usuarios
CREATE TABLE rol (
    id_rol SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    id_rol INT NOT NULL REFERENCES rol(id_rol)
);

-- 2. Tablas Catálogo (Paramétricas / Diccionarios)
CREATE TABLE sucursal (
    id_sucursal SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE departamento (
    id_departamento SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE marca (
    id_marca SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE modelo (
    id_modelo SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_marca INT NOT NULL REFERENCES marca(id_marca)
);

CREATE TABLE tipo_equipo (
    id_tipo SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE estado_equipo (
    id_estado SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- 3. Tabla Central de Inventario
CREATE TABLE activo (
    id_activo SERIAL PRIMARY KEY,
    placa VARCHAR(50) UNIQUE NOT NULL,
    serie VARCHAR(100) UNIQUE NOT NULL,
    mac VARCHAR(50) NULL,
    posicion_monitor VARCHAR(50) NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_tipo INT NOT NULL REFERENCES tipo_equipo(id_tipo),
    id_marca INT NOT NULL REFERENCES marca(id_marca),
    id_modelo INT NOT NULL REFERENCES modelo(id_modelo),
    id_estado INT NOT NULL REFERENCES estado_equipo(id_estado),
    id_sucursal INT NOT NULL REFERENCES sucursal(id_sucursal),
    id_departamento INT NOT NULL REFERENCES departamento(id_departamento),
    id_usuario INT REFERENCES usuario(id_usuario) -- Puede ser NULL si está en bodega sin asignar
);

-- 4. Tabla de Trazabilidad e Historial
CREATE TABLE bitacora_auditoria (
    id_evento SERIAL PRIMARY KEY,
    accion VARCHAR(50) NOT NULL,
    detalle TEXT NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_activo INT NOT NULL REFERENCES activo(id_activo),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario) -- El usuario que ejecutó la acción
);

-- 5. Índices de optimización (Para búsquedas rápidas)
CREATE INDEX idx_activo_serie ON activo(serie);
CREATE INDEX idx_activo_placa ON activo(placa);
CREATE INDEX idx_bitacora_activo ON bitacora_auditoria(id_activo);

-- Roles iniciales requeridos por la aplicación.
INSERT INTO rol (nombre)
VALUES ('ADMINISTRADOR'), ('ENCARGADO_INVENTARIO'), ('CONSULTA')
ON CONFLICT (nombre) DO NOTHING;