BASE_URL = "/api/v1"

# ==================================================
# AUTHENTICATIONS
# ==================================================

# POST /authentication/login
# LoginRequest -> LoginResponse

POST_LOGIN = f"{BASE_URL}/authentication/login"

# POST /authentication/refresh
# LoginResponse

POST_REFRESH_TOKEN = f"{BASE_URL}/authentication/refresh"

# GET /authentication/me
# Usuario autenticado

GET_CURRENT_USER = f"{BASE_URL}/authentication/me"

# POST /authentication/logout

POST_LOGOUT = f"{BASE_URL}/authentication/logout"


# ==================================================
# USUARIOS
# ==================================================

# GET /usuarios
# Listar usuarios

GET_USUARIOS = f"{BASE_URL}/usuarios"

# POST /usuarios
# Crear usuario

POST_USUARIO = f"{BASE_URL}/usuarios"

# GET /usuarios/{id_usuario}
# Obtener usuario

GET_USUARIO_BY_ID = f"{BASE_URL}/usuarios/{{id_usuario}}"

# PUT /usuarios/{id_usuario}
# Modificar usuario

PUT_USUARIO = f"{BASE_URL}/usuarios/{{id_usuario}}"

# DELETE /usuarios/{id_usuario}
# Eliminar usuario

DELETE_USUARIO = f"{BASE_URL}/usuarios/{{id_usuario}}"

# PATCH /usuarios/{id_usuario}/activar
# Activar usuario

PATCH_ACTIVAR_USUARIO = (
    f"{BASE_URL}/usuarios/{{id_usuario}}/activar"
)

# PATCH /usuarios/{id_usuario}/desactivar
# Desactivar usuario

PATCH_DESACTIVAR_USUARIO = (
    f"{BASE_URL}/usuarios/{{id_usuario}}/desactivar"
)


# ==================================================
# ROLES
# ==================================================

# GET /roles
# Listar roles

GET_ROLES = f"{BASE_URL}/roles"

# POST /roles
# Crear rol

POST_ROL = f"{BASE_URL}/roles"

# GET /roles/{id_rol}
# Obtener rol

GET_ROL_BY_ID = f"{BASE_URL}/roles/{{id_rol}}"

# PUT /roles/{id_rol}
# Modificar rol

PUT_ROL = f"{BASE_URL}/roles/{{id_rol}}"

# DELETE /roles/{id_rol}
# Eliminar rol

DELETE_ROL = f"{BASE_URL}/roles/{{id_rol}}"


# ==================================================
# ACTIVOS
# ==================================================

# GET /activos
# Listar activos

GET_ACTIVOS = f"{BASE_URL}/activos"

# POST /activos
# Registrar activo

POST_ACTIVO = f"{BASE_URL}/activos"

# GET /activos/busqueda
# Busqueda avanzada

GET_BUSQUEDA_ACTIVOS = f"{BASE_URL}/activos/busqueda"

# Query Params:
# placa
# serie
# usuario
# departamento
# sucursal
# estado
# tipo

# GET /activos/{id_activo}
# Obtener activo

GET_ACTIVO_BY_ID = f"{BASE_URL}/activos/{{id_activo}}"

# PUT /activos/{id_activo}
# Modificar activo

PUT_ACTIVO = f"{BASE_URL}/activos/{{id_activo}}"

# DELETE /activos/{id_activo}
# Baja logica

DELETE_ACTIVO = f"{BASE_URL}/activos/{{id_activo}}"

# GET /activos/{id_activo}/historial
# Historial del activo

GET_HISTORIAL_ACTIVO = (
    f"{BASE_URL}/activos/{{id_activo}}/historial"
)


# ==================================================
# AUDITORIA
# ==================================================

# GET /auditoria
# Consultar auditoria

GET_AUDITORIA = f"{BASE_URL}/auditoria"

# GET /auditoria/{id_evento}
# Obtener evento de auditoria

GET_EVENTO_AUDITORIA = (
    f"{BASE_URL}/auditoria/{{id_evento}}"
)


# ==================================================
# DASHBOARD
# ==================================================

# GET /dashboard/resumen

GET_DASHBOARD_RESUMEN = (
    f"{BASE_URL}/dashboard/resumen"
)


# ==================================================
# SISTEMA
# ==================================================

# GET /health

GET_HEALTH = f"{BASE_URL}/health"

# GET /version

GET_VERSION = f"{BASE_URL}/version"