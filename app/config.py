from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    HUGGINGFACEHUB_API_TOKEN: str

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()