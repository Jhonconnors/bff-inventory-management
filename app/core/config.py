"""Configuración de aplicación a partir de variables de entorno."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""Parámetros centralizados del servicio."""

	app_name: str = "MVP Inventario Trazable"
	api_prefix: str = "/api/v1"
	database_url: str = Field(min_length=1)
	jwt_secret_key: str = Field(default="local-development-only-change-this-secret-32", min_length=32)
	jwt_algorithm: str = "HS256"
	access_token_expire_minutes: int = 30
	refresh_token_expire_days: int = 7
	cors_origins: list[str] = ["http://localhost:3000"]

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
	"""Devuelve una instancia cacheada de configuración."""
	return Settings()


settings = get_settings()
