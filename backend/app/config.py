from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    DEFAULT_USER_ID: int = 1

    class Config:
        env_file = ".env"


settings = Settings()
