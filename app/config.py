import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database settings
    POSTGRES_DB: str = os.getenv('POSTGRES_DB', 'bughunter')
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', '')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT: int = int(os.getenv('POSTGRES_PORT', 5432))
    SQLITE_PATH: str = os.getenv('SQLITE_PATH', 'data/bughunter.db')

    # Authentication settings
    AUTH_SECRET_KEY: str = os.getenv('AUTH_SECRET_KEY', 'default-secret-key')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

    # Email notification settings
    SMTP_HOST: str = os.getenv('SMTP_HOST', 'smtp.example.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER: str = os.getenv('SMTP_USER')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD')
    FROM_EMAIL: str = os.getenv('FROM_EMAIL', 'noreply@example.com')

    # API settings
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', 8000))

    # AI settings
    AI_MODEL_NAME: str = os.getenv('AI_MODEL_NAME', 'gpt2')
    AI_COMPRESSED_MODEL_NAME: str = os.getenv('AI_COMPRESSED_MODEL_NAME', 'distilgpt2')
    AI_MAX_RESPONSE_LENGTH: int = int(os.getenv('AI_MAX_RESPONSE_LENGTH', 100))
    AI_TEMPERATURE: float = float(os.getenv('AI_TEMPERATURE', 0.7))
    AI_MIN_REQUEST_INTERVAL: float = float(os.getenv('AI_MIN_REQUEST_INTERVAL', 0.1))

    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()
