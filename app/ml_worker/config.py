from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # RabbitMQ settings
    RABBITMQ_USER: Optional[str] = None
    RABBITMQ_PASSWORD: Optional[str] = None
    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_PORT: Optional[int] = None
        
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    def validate(self) -> None:
        """Validate critical configuration settings"""
        if not all([self.RABBITMQ_USER, self.RABBITMQ_PASSWORD, self.RABBITMQ_HOST, self.RABBITMQ_PORT]):
            raise ValueError("Missing required database configuration")

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings
