from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: Optional[str] = None
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    vector_db_path: str = ".index/"
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
