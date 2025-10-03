from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    env: str = "local"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings(_env_file=".env")


