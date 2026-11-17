# SIGATI+ Backend

API FastAPI con SQLAlchemy 2, PostgreSQL, Pydantic v2, JWT y Alembic. La API se publica bajo `/api/v1`.

## Ejecución local

1. Use Python 3.12 y PostgreSQL.
2. Instale dependencias: `python -m pip install -r requirements.txt`.
3. Configure las variables de `.env.example` en su entorno. `JWT_SECRET_KEY` debe ser un secreto aleatorio y exclusivo por ambiente.
4. Aplique el esquema inicial: `alembic upgrade head`.
5. Inicie la API: `uvicorn app.main:app --reload`.

Swagger UI queda disponible en `/docs`. Los roles iniciales se crean mediante la primera migración. Cree el administrador inicial en una consola confiable con `python -m app.bootstrap_admin`; la contraseña se solicita sin mostrarla y no hay credenciales predeterminadas.

## Docker

Defina `JWT_SECRET_KEY` en el ambiente y ejecute `docker compose up --build`. La API espera a que PostgreSQL esté saludable y aplica las migraciones antes de iniciar Uvicorn.

## Seguridad y auditoría

Los endpoints de auditoría son de solo lectura y cada operación de activo que modifica el inventario inserta su evento en la misma transacción. `DELETE` de activos es lógico y conserva el registro con estado de baja. Los detalles de baja (resolución, fecha y motivo) se guardan en el detalle JSON de auditoría, ya que el esquema físico definido no agrega columnas a `activos`.

Los JWT son stateless. El endpoint de logout confirma el cierre en el cliente, pero un token ya emitido sigue siendo válido hasta su expiración; revocación inmediata requiere almacenamiento adicional de sesiones o una lista de revocación externa.