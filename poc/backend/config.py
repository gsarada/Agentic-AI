from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

POC_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=POC_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Personal Stylist POC"
    debug: bool = True
    secret_key: str = "change-me"
    database_url: str = f"sqlite:///{POC_ROOT / 'database.sqlite'}"

    upload_dir: Path = POC_ROOT / "images" / "uploads"
    generated_dir: Path = POC_ROOT / "images" / "generated"

    llm_provider: str = "openai"
    openai_api_key: str = ""
    model: str = "gpt-4o-mini"

    tryon_provider: str = "mock"
    idm_vton_api_url: str = ""
    idm_vton_api_key: str = ""

    access_token_expire_minutes: int = 1440


@lru_cache
def get_settings() -> Settings:
    return Settings()
