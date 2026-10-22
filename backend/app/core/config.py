from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Gestión de Eventos Universitarios"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./universidad_eventos.db"
    SECRET_KEY: str = "universidad-super-secret-key-2026-sdd"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
