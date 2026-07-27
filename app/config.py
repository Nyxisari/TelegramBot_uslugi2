from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    ACCOUNT_SETTINGS: str
    GOOGLE_SHEET: str

    class Config:
        env_file = ".env"


settings = Settings()