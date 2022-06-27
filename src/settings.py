from pydantic import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    BASE_DIR: Path = BASE_DIR
    API_TOKEN: str

    class Config:
        env_file = '.env'


settings = Settings()
