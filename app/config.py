from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        case_sensitive=True
    )

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    CORS_ORIGINS: list[str]

    # @field_validator("CORS_ORIGINS", mode="before")
    # @classmethod
    # def parse_cors(cls, v: Any) -> list[str]:
    #     if isinstance(v, str):
    #         return [origin.strip() for origin in v.split(",")]
    #     return v

settings = Settings()