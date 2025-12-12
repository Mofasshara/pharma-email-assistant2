from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
