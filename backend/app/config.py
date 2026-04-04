from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    DEFAULT_USER_ID: int = 1
    OPENROUTER_API_KEY: str = ""
    LLM_MODEL: str = "qwen/qwen3.6-plus:free"

    class Config:
        env_file = ".env"


settings = Settings()
