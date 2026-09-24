from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = 'NHAA RSTAM'
    VERSION: str = '1.0.0'
    DEBUG: bool = True
    DATABASE_URL: str = 'sqlite:///./rstam.db'
    ENCRYPTION_KEY: str = 'change-me-in-production-32bytes!'
    WHISPER_MODEL_SIZE: str = 'base'
    MAX_AUDIO_SIZE_MB: int = 50
    AUDIO_RETENTION_DAYS: int = 90
    CONSENT_REQUIRED: bool = True
    SUPPORTED_LANGUAGES: list[str] = ['en', 'hi', 'ta', 'te', 'mr', 'bn', 'kn', 'gu', 'ml', 'pa', 'or', 'ur']
    CORS_ORIGINS: list[str] = ['http://localhost:5173', 'http://localhost:3000', '*']

    class Config:
        env_file = ".env"

settings = Settings()
