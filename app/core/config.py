from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ph-admin-system"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"


settings = Settings()
