-- Datos de prueba MVP Inventario Trazable para PostgreSQL.
-- Ejecutar en pgAdmin conectado a inventario_tecnologico.
-- Solo usar en desarrollo/QA. El script es repetible e inserta solo faltantes.
-- Password para todas las cuentas de prueba: SigatiDemo123!

BEGIN;

-- Roles
INSERT INTO rol (nombre)
VALUES
    ('ADMINISTRADOR'),
    ('ENCARGADO_INVENTARIO'),
    ('MESA_SERVICIOS'),
    ('CONSULTA')
ON CONFLICT (nombre) DO NOTHING;

-- Usuarios de prueba. El password_hash corresponde a SigatiDemo123! (bcrypt).
INSERT INTO usuario (nombre, correo, password_hash, activo, id_rol)
SELECT
    demo.nombre,
    demo.correo,
    '$2b$12$peC3nERzogDKTEX9/XE8.Ofrzs8.664YDk8wZLM6wxOLPTnGp4zQq',
    TRUE,
    r.id_rol
FROM (
    VALUES
        ('Administrador de prueba', 'sigati.admin@example.com', 'ADMINISTRADOR'),
        ('Encargado de inventario de prueba', 'sigati.inventario@example.com', 'ENCARGADO_INVENTARIO'),
        ('Mesa de servicios de prueba', 'sigati.mesa@example.com', 'MESA_SERVICIOS'),
        ('Usuario de consulta de prueba', 'sigati.consulta@example.com', 'CONSULTA')
) AS demo(nombre, correo, nombre_rol)
JOIN rol AS r ON r.nombre = demo.nombre_rol
ON CONFLICT (correo) DO NOTHING;

-- Sucursales
INSERT INTO sucursal (nombre)
SELECT demo.nombre
FROM (VALUES ('Casa Matriz'), ('Sucursal Norte')) AS demo(nombre)
WHERE NOT EXISTS (
    SELECT 1 FROM sucursal AS existente WHERE existente.nombre = demo.nombre
);

-- Departamentos
INSERT INTO departamento (nombre)
SELECT demo.nombre
FROM (VALUES ('Tecnologia'), ('Bodega')) AS demo(nombre)
WHERE NOT EXISTS (
    SELECT 1 FROM departamento AS existente WHERE existente.nombre = demo.nombre
);

-- Marcas
INSERT INTO marca (nombre)
SELECT demo.nombre
FROM (VALUES ('Lenovo'), ('Dell')) AS demo(nombre)
WHERE NOT EXISTS (
    SELECT 1 FROM marca AS existente WHERE existente.nombre = demo.nombre
);

-- Modelos
INSERT INTO modelo (nombre, id_marca)
SELECT demo.nombre_modelo, m.id_marca
FROM (
    VALUES ('ThinkPad E14', 'Lenovo'), ('OptiPlex 7010', 'Dell')
) AS demo(nombre_modelo, nombre_marca)
JOIN marca AS m ON m.nombre = demo.nombre_marca
WHERE NOT EXISTS (
    SELECT 1
    FROM modelo AS existente
    WHERE existente.nombre = demo.nombre_modelo
      AND existente.id_marca = m.id_marca
);

-- Tipos de equipo
INSERT INTO tipo_equipo (nombre)
SELECT demo.nombre
FROM (VALUES ('Notebook'), ('Computador de escritorio')) AS demo(nombre)
WHERE NOT EXISTS (
    SELECT 1 FROM tipo_equipo AS existente WHERE existente.nombre = demo.nombre
);

-- Estados
INSERT INTO estado_equipo (nombre)
SELECT demo.nombre
FROM (VALUES ('Disponible en bodega'), ('Asignado'), ('Baja')) AS demo(nombre)
WHERE NOT EXISTS (
    SELECT 1 FROM estado_equipo AS existente WHERE existente.nombre = demo.nombre
);

-- Activos: uno asignado y otro disponible en bodega.
INSERT INTO activo (
    placa, serie, mac, posicion_monitor, id_tipo, id_marca, id_modelo,
    id_estado, id_sucursal, id_departamento, id_usuario
)
SELECT
    demo.placa,
    demo.serie,
    demo.mac,
    demo.posicion_monitor,
    t.id_tipo,
    m.id_marca,
    mo.id_modelo,
    e.id_estado,
    s.id_sucursal,
    d.id_departamento,
    u.id_usuario
FROM (
    VALUES
        ('DEMO-SIGATI-001', 'DEMO-SERIE-001', '02:00:00:00:00:01', 'Piso 1 - puesto 01', 'Notebook', 'Lenovo', 'ThinkPad E14', 'Asignado', 'Casa Matriz', 'Tecnologia', 'sigati.inventario@example.com'),
        ('DEMO-SIGATI-002', 'DEMO-SERIE-002', '02:00:00:00:00:02', NULL, 'Computador de escritorio', 'Dell', 'OptiPlex 7010', 'Disponible en bodega', 'Casa Matriz', 'Bodega', NULL)
) AS demo(placa, serie, mac, posicion_monitor, tipo, marca, modelo, estado, sucursal, departamento, correo_usuario)
JOIN tipo_equipo AS t ON t.nombre = demo.tipo
JOIN marca AS m ON m.nombre = demo.marca
JOIN modelo AS mo ON mo.nombre = demo.modelo AND mo.id_marca = m.id_marca
JOIN estado_equipo AS e ON e.nombre = demo.estado
JOIN sucursal AS s ON s.nombre = demo.sucursal
JOIN departamento AS d ON d.nombre = demo.departamento
LEFT JOIN usuario AS u ON u.correo = demo.correo_usuario
WHERE NOT EXISTS (
    SELECT 1 FROM activo AS existente WHERE existente.placa = demo.placa
)
ON CONFLICT DO NOTHING;

-- Auditoría de creación para los activos de prueba.
INSERT INTO bitacora_auditoria (accion, detalle, id_activo, id_usuario)
SELECT
    'CREATE',
    json_build_object('origen', 'datos_prueba.sql', 'placa', a.placa)::TEXT,
    a.id_activo,
    admin.id_usuario
FROM activo AS a
CROSS JOIN usuario AS admin
WHERE a.placa IN ('DEMO-SIGATI-001', 'DEMO-SIGATI-002')
  AND admin.correo = 'sigati.admin@example.com'
  AND NOT EXISTS (
      SELECT 1
      FROM bitacora_auditoria AS existente
      WHERE existente.id_activo = a.id_activo
        AND existente.accion = 'CREATE'
        AND existente.detalle = json_build_object('origen', 'datos_prueba.sql', 'placa', a.placa)::TEXT
  );

-- Auditoría de asignación del primer activo.
INSERT INTO bitacora_auditoria (accion, detalle, id_activo, id_usuario)
SELECT
    'ASSIGN',
    json_build_object(
        'origen', 'datos_prueba.sql',
        'nota_interna', 'Asignacion de prueba',
        'correo_responsable', u.correo
    )::TEXT,
    a.id_activo,
    admin.id_usuario
FROM activo AS a
JOIN usuario AS u ON u.id_usuario = a.id_usuario
CROSS JOIN usuario AS admin
WHERE a.placa = 'DEMO-SIGATI-001'
  AND admin.correo = 'sigati.admin@example.com'
  AND NOT EXISTS (
      SELECT 1
      FROM bitacora_auditoria AS existente
      WHERE existente.id_activo = a.id_activo
        AND existente.accion = 'ASSIGN'
        AND existente.detalle = json_build_object(
            'origen', 'datos_prueba.sql',
            'nota_interna', 'Asignacion de prueba',
            'correo_responsable', u.correo
        )::TEXT
  );

COMMIT;

-- Cuentas creadas (password para todas: SigatiDemo123!):
-- sigati.admin@example.com
-- sigati.inventario@example.com
-- sigati.mesa@example.com
-- sigati.consulta@example.com
