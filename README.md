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

## Despliegue local con Docker

1. Instala Docker Desktop desde [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) e inicia Docker Desktop. En Windows, usa el backend WSL 2 si el instalador lo solicita.
2. Verifica la instalación en PowerShell:

   ```powershell
   docker --version
   docker compose version
   ```

3. En esta carpeta, conserva en `.env` los mismos valores de desarrollo para `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` y `JWT_SECRET_KEY`. Si aún no tienes ese archivo, créalo con esas cuatro variables y completa los valores de tu entorno local. No publiques ni compartas el archivo. Docker usa las credenciales de PostgreSQL tanto para iniciar la base como para conectar la API.
4. Desde la raíz del proyecto, cambia a la carpeta del backend:

   ```powershell
   Set-Location .\bff-inventory-management
   ```

5. Construye las imágenes e inicia los tres contenedores:

   ```powershell
   docker compose up --build -d
   ```

   El servicio `db` construye la imagen desde `database/Dockerfile`, crea la base definida por `POSTGRES_DB` y ejecuta `01-esquema.sql` y `02-datos-prueba.sql` en una base nueva. El servicio `api` aplica las migraciones Alembic y publica FastAPI. El servicio `frontend` construye el MFE y Nginx reenvía `/api` al backend.
6. Comprueba el estado:

   ```powershell
   docker compose ps
   docker compose logs -f db api frontend
   ```

7. Abre:
   - Frontend: `http://localhost:3000`
   - Swagger del backend: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/api/v1/health`
   - PostgreSQL desde una herramienta local: `localhost:5432`, con las credenciales del `.env`.

Los usuarios y roles de demostración provienen de `database/02-datos-prueba.sql` y conservan la contraseña de desarrollo `SigatiDemo123!`. La carpeta `database/` contiene también `00-crear-base-manual.sql` para uso manual con pgAdmin; no se ejecuta en Docker porque la imagen oficial crea la base a partir de `POSTGRES_DB`.

Los scripts de inicialización de PostgreSQL solo se ejecutan cuando el volumen de datos está vacío. `docker compose down` detiene los servicios sin borrar la base. **`docker compose down -v` elimina permanentemente el volumen y todos sus datos**, y solo debe usarse cuando se quiera reiniciar la base desde cero.

Las imágenes `sigati-db:local`, `sigati-api:local` y `sigati-frontend:local` se construyen y quedan disponibles en el almacenamiento local de Docker; los `Dockerfile` están en las carpetas `database/`, backend y frontend, respectivamente.

## Carga de datos de prueba

En pgAdmin, conéctate a la base `inventario_tecnologico`, abre **Query Tool**, carga `database/02-datos-prueba.sql` y ejecuta todo el archivo. El SQL inserta datos idempotentemente en las diez tablas dentro de una transacción. Es solo para desarrollo/QA.

Las cuentas demo usan la contraseña `SigatiDemo123!`:

- `sigati.admin@example.com` (rol `ADMINISTRADOR`)
- `sigati.inventario@example.com` (rol `ENCARGADO_INVENTARIO`)
- `sigati.consulta@example.com` (rol `CONSULTA`)

## Postman

Importa `MVP Inventario Trazable Postman.json`. La variable `baseUrl` usa por defecto `http://localhost:8000/api/v1`. Ejecuta **Authentication / POST Login** para que Postman guarde el access token y refresh token en las variables de colección. Ajusta las variables `id_*` si los identificadores de tu base de datos no empiezan en 1.

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

`app/` contiene modelos, schemas, controllers, services, repositories, seguridad y configuración. `migrations/` mantiene el esquema Alembic. `database/` contiene los scripts SQL y el Dockerfile de PostgreSQL. `swagger.yml` es la especificación OpenAPI fuente y `MVP Inventario Trazable Postman.json` contiene las solicitudes para probar la API.

En usuarios, `PATCH /api/v1/usuarios/{id_usuario}/desactivar` conserva la cuenta y la oculta de las consultas de usuarios activos. `DELETE /api/v1/usuarios/{id_usuario}` la elimina permanentemente solo si no tiene eventos de auditoría ni activos asignados; el usuario autenticado tampoco puede eliminar su propia cuenta. Para conservar referencias históricas, desactiva en vez de eliminar cuentas que ya tengan actividad.

Los roles predefinidos son `ADMINISTRADOR`, `ENCARGADO_INVENTARIO` y `CONSULTA`. `ADMINISTRADOR` tiene acceso total; `ENCARGADO_INVENTARIO` puede realizar operaciones de activos y catálogos y consultar usuarios y roles, sin modificarlos. `CONSULTA` y roles personalizados pueden consultar los módulos generales, pero no usuarios ni roles, y no tienen permisos de escritura. Estas reglas se validan en los endpoints y sustituyen cualquier descripción general previa de la autorización en este documento.

El listado de usuarios oculta cuentas inactivas de forma predeterminada. Los administradores pueden incluirlas mediante `GET /api/v1/usuarios?include_inactive=true`; `PUT /api/v1/usuarios/{id_usuario}` permite cambiar `activo` para desactivar o reactivar la cuenta.

## Seguridad y alcance

La API usa JWT bearer. Las cuentas autenticadas tienen permisos según su rol; el rol `CONSULTA` es de solo lectura y las modificaciones de activos están restringidas a `ADMINISTRADOR`. Logout requiere el access token en el header Bearer y el refresh token en el body, y revoca ambos. La lista de revocación vive en memoria: es adecuada para el proceso único del MVP, pero se pierde al reiniciar y no se comparte entre múltiples workers/instancias. Para desplegar escalado horizontal debe sustituirse por almacenamiento compartido. La bitácora es inmutable desde la API y las modificaciones de activos insertan su evento en la misma transacción.

Las contraseñas aceptan hasta 255 caracteres. Los hashes nuevos usan bcrypt con prehash SHA-256 versionado; los hashes bcrypt existentes continúan verificándose.

El MVP no incluye dashboard gerencial, QR, alertas de obsolescencia ni funciones predictivas.