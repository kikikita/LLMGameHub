from dotenv import load_dotenv

load_dotenv()
from pydantic_settings import BaseSettings
import logging
from pydantic import SecretStr

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t%(asctime)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
)

class BaseAppSettings(BaseSettings):
    """Base settings class with common configuration."""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
class AppSettings(BaseAppSettings):
    gemini_api_key: SecretStr
    top_p: float = 0.95
    temperature: float = 0.5
    

settings = AppSettings()
