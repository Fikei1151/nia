import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    google_api_key: str = "YOUR_GOOGLE_API_KEY"
    database_url: str = "postgresql+asyncpg://user:password@host:port/dbname"

settings = Settings() 