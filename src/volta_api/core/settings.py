from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int = 587

    class Config:
        env_file = ".env"


settings = Settings()
