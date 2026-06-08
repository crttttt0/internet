from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    NAME: str = "Internet"
    VERSION: str = "1.0.0"
    SUMMARY: str = 'База пользователей ЛВС "ИНТЕРНЕТ"'
    DEBUG: bool = True
    ECHO: bool = True


class DatabaseSettings(BaseSettings):
    URL: SecretStr
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_PRE_PING: bool = True


class JWTSettings(BaseSettings):
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    database: DatabaseSettings
    jwt: JWTSettings

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )


settings = Settings()
