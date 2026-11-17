"""Excepciones de negocio traducibles a respuestas HTTP."""


class AppError(Exception):
    """Error de aplicación con estado HTTP y detalle legible."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    """Entidad solicitada inexistente."""

    def __init__(self, message: str) -> None:
        super().__init__(message, 404)


class ConflictError(AppError):
    """Conflicto de unicidad o integridad de negocio."""

    def __init__(self, message: str) -> None:
        super().__init__(message, 409)


class UnauthorizedError(AppError):
    """Credenciales o sesión no válidas."""

    def __init__(self, message: str) -> None:
        super().__init__(message, 401)


class BusinessRuleError(AppError):
    """Operación que viola una regla de negocio."""

    def __init__(self, message: str) -> None:
        super().__init__(message, 422)