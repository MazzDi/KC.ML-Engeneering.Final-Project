from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Настройки приложения (база данных, RabbitMQ, приложение)"""
    # Database settings
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    # RabbitMQ settings
    RABBITMQ_USER: Optional[str] = None
    RABBITMQ_PASSWORD: Optional[str] = None
    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_PORT: Optional[int] = None
    
    # Application settings
    APP_NAME: Optional[str] = None
    APP_DESCRIPTION: Optional[str] = None
    DEBUG: Optional[bool] = None
    API_VERSION: Optional[str] = None
    BOT_TOKEN: Optional[str] = None
    
    @property
    def DATABASE_URL_asyncpg(self):
        """Возвращает URL базы данных для asyncpg драйвера"""
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
    
    @property
    def DATABASE_URL_psycopg(self):
        """Возвращает URL базы данных для psycopg2 драйвера"""
        return f'postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    def validate(self) -> None:
        """Проверяет критически важные настройки конфигурации"""
        if not all([self.POSTGRES_HOST, self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
            raise ValueError("Missing required database configuration")
        if not all([self.RABBITMQ_USER, self.RABBITMQ_PASSWORD, self.RABBITMQ_HOST, self.RABBITMQ_PORT]):
            raise ValueError("Missing required RabbitMQ configuration")

@lru_cache()
def get_settings() -> Settings:
    """Получает настройки приложения с кэшированием"""
    settings = Settings()
    settings.validate()
    return settings
