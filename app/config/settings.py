from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

class Settings(BaseSettings):
    API_VERSION: str = "v1"
    DEBUG_MODE: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.1"  # เปลี่ยนเป็น model ที่รองรับ
    TOGETHER_API_KEY: str = Field(..., description="Together API Key")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'