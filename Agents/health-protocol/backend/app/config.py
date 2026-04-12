from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

# Resolve .env relative to this file so uvicorn can be launched from any
# working directory (project root OR backend/).
# config.py lives at  <root>/backend/app/config.py → root is three parents up.
_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    anthropic_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./data/health_protocol.db"
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    cors_origins: str = "http://localhost:5173,http://localhost:5174,capacitor://localhost"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str) -> str:
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
