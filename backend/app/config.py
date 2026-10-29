import os
from pydantic_settings import BaseSettings
from typing import List


DEFAULT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../smartverify.db"))


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    SECRET_KEY: str = "smartverify-prototype-secret-key-do-not-use-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Storage settings
    UPLOAD_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/uploads"))
    SYNTHETIC_DATA_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/synthetic"))
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: str = "pdf,png,jpg,jpeg,csv"
    
    # OCR
    OCR_ENGINE: str = "pymupdf_fallback"
    TESSERACT_CMD: str = "tesseract"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_extensions_set(self) -> set:
        return {ext.strip().lower().lstrip(".") for ext in self.ALLOWED_EXTENSIONS.split(",")}

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
