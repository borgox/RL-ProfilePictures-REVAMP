import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    steam_api_key: Optional[str] = None
    psn_npsso_token: Optional[str] = None
    
    # Admin settings
    admin_secret: str = "change_this_secret_key"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql+asyncpg://username:password@localhost:5432/rlpfp_db"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "rlpfp_db"
    database_user: str = "username"
    database_password: str = "password"
    
    # Cache settings
    cache_dir: str = "cache"
    max_cache_size_mb: int = 0  # 0 = unlimited cache size
    
    # Rate limiting
    rate_limit_requests: int = 40
    rate_limit_window: int = 60  # seconds
    
    # Image settings  
    target_image_width: int = 48
    target_image_height: int = 48
    image_quality: int = 95
    
    @property
    def target_image_size(self) -> tuple:
        return (self.target_image_width, self.target_image_height)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
