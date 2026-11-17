# MVP Inventario Trazable

Backend REST para el MVP de gestión de activos tecnológicos. Usa Python 3.12, FastAPI, Pydantic v2, SQLAlchemy y PostgreSQL. La API se publica bajo `/api/v1`.

## Inicio local

1. Instala Python 3.12 y PostgreSQL.
2. Instala dependencias: `python -m pip install -r requirements.txt`.
3. Configura `DATABASE_URL` y `JWT_SECRET_KEY` en el archivo local `.env` de la raíz. No subas ese archivo al repositorio.
4. Aplica la migración inicial: `python -m alembic upgrade head`.
5. Inicia FastAPI: `python -m uvicorn app.main:app --reload`.

La URL de PostgreSQL tiene el formato `postgresql+psycopg2://USUARIO:CLAVE@HOST:5432/BASE`. La aplicación y Alembic leen la misma variable `DATABASE_URL`; no hay una URL de BD escrita en el código. Si el esquema del modelo físico ya se creó desde pgAdmin, la migración registra la revisión y agrega los roles iniciales que falten.

La documentación interactiva está en `http://localhost:8000/docs`; el health check es `http://localhost:8000/api/v1/health`.

## Docker

Con `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y `JWT_SECRET_KEY` configurados en `.env`, inicia PostgreSQL y la API con `docker compose up --build`. Dentro de Docker la API usa el host `db`; desde el equipo local PostgreSQL queda publicado en `localhost:5432`. El contenedor de API aplica Alembic antes de iniciar Uvicorn.

## Carga de datos de prueba

En pgAdmin, conéctate a la base `inventario_tecnologico`, abre **Query Tool**, carga `datos_prueba.sql` y ejecuta todo el archivo. El SQL inserta datos idempotentemente en las diez tablas dentro de una transacción. Es solo para desarrollo/QA.

Las cuentas demo usan la contraseña `SigatiDemo123!`:

- `sigati.admin@example.com` (rol `ADMINISTRADOR`)
- `sigati.inventario@example.com` (rol `ENCARGADO_INVENTARIO`)
- `sigati.mesa@example.com` (rol `MESA_SERVICIOS`)
- `sigati.consulta@example.com` (rol `CONSULTA`)

## Postman

Importa `SIGATI.postman_collection.json`. La variable `baseUrl` usa por defecto `http://localhost:8000/api/v1`. Ejecuta **Authentication / POST Login** para que Postman guarde el access token y refresh token en las variables de colección. Ajusta las variables `id_*` si los identificadores de tu base de datos no empiezan en 1.

## Controllers y tablas

Los controllers reciben y validan requests, delegan la lógica a los services y serializan respuestas. Las operaciones de escritura y sus validaciones están en `app/services`; SQLAlchemy se accede desde los repositories. Las tablas indicadas a continuación usan los nombres singulares del modelo físico.

| Controller | Responsabilidad | Tablas consultadas o modificadas |
| --- | --- | --- |
| `authentication_controller` | Login, refresh, logout y perfil autenticado. | `usuario` (y `rol` al validar permisos). |
| `usuarios_controller` | CRUD, activación y baja lógica de usuarios. | `usuario`, `rol` (validación de `id_rol`). |
| `roles_controller` | CRUD de roles. | `rol`. |
| `activos_controller` | CRUD, búsqueda, historial, asignación, traslado, devolución y baja. | `activo`; consulta `tipo_equipo`, `marca`, `modelo`, `estado_equipo`, `sucursal`, `departamento`, `usuario`; inserta en `bitacora_auditoria` en cambios. |
| `auditoria_controller` | Consulta paginada de eventos y consulta por ID; no permite escritura. | Solo lectura de `bitacora_auditoria`. |
| `sucursales_controller` | CRUD de sucursales. | `sucursal`. |
| `departamentos_controller` | CRUD de departamentos. | `departamento`. |
| `marcas_controller` | CRUD de marcas. | `marca`. |
| `modelos_controller` | CRUD de modelos y validación de marca asociada. | `modelo`, `marca`. |
| `tipos_equipo_controller` | CRUD del catálogo de tipos. | `tipo_equipo`. |
| `estados_equipo_controller` | CRUD del catálogo de estados. | `estado_equipo`. |
| Endpoints de sistema en `main.py` | Health check y versión. | Ninguna tabla. |

`app/` contiene modelos, schemas, controllers, services, repositories, seguridad y configuración. `migrations/` mantiene el esquema Alembic. `swagger.yml` es la especificación OpenAPI fuente y `SIGATI.postman_collection.json` contiene las solicitudes para probar la API.

## Seguridad y alcance

La API usa JWT bearer. Las cuentas autenticadas tienen permisos según su rol; el rol `CONSULTA` es de solo lectura y las modificaciones de activos están restringidas a `ADMINISTRADOR`. La bitácora es inmutable desde la API y las modificaciones de activos insertan su evento en la misma transacción.

El MVP no incluye dashboard gerencial, QR, alertas de obsolescencia ni funciones predictivas.