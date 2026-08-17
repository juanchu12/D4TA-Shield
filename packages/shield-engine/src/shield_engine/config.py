"""Runtime configuration for the Shield analysis engine."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.0

    data_dir: Path = Path(__file__).resolve().parents[2] / "data"
    db_path: Path | None = None
    internal_token: str = "dev-internal-token"
    host: str = "0.0.0.0"
    port: int = 8080
    enable_ocr: bool = True
    ocr_lang: str = "spa+eng"

    @property
    def sqlite_path(self) -> Path:
        if self.db_path:
            return self.db_path
        path = self.data_dir / "shield.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def uploads_dir(self) -> Path:
        path = self.data_dir / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def validate_openai_key(self) -> None:
        if not self.openai_api_key or not self.openai_api_key.strip():
            raise ValueError("OPENAI_API_KEY is not configured.")


settings = Settings()
