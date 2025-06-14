import logging
from pathlib import Path

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent
SQLITE_URL = "sqlite+aiosqlite:///./database.db"


class Token(BaseModel):
    private_key_path: Path = BASE_DIR.parent / "secrets" / "private.pem"
    public_key_path: Path = BASE_DIR.parent / "secrets" / "public.pem"
    access_expire_minutes: int = 60
    refresh_expire_minutes: int = 60 * 24 * 30
    reset_password_expire_minutes: int = 30
    registration_confirmation_expire_minutes: int = 30
    algorithm: str = "RS256"


class Superuser(BaseModel):
    name: str = "admin"
    password: str = "changeme"


class Database(BaseModel):
    username: str
    password: str
    db: str
    hostname: str
    port: int = 5432
    driver: str = "asyncpg"
    system: str = "postgresql"


class Redis(BaseModel):
    host: str
    port: int = 6379
    db: int = 1
    username: str | None = None
    password: str | None = None


class Email(BaseModel):
    email: str
    name: str | None = None
    user: str | None = None
    password: str | None = None
    host: str
    port: int
    tls: bool = False
    ssl: bool = False

    @field_validator("name", "user")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        if value is None:
            return cls.email
        return value


class Api(BaseModel):
    v1: str = "/api/v1"


class App(BaseModel):
    protocol: str = "http"
    host: str = "127.0.0.1"
    port: int = 8000
    name: str = "Wishix"
    registration: bool = True
    api: Api = Api()

    @field_validator("protocol", mode="before")
    @classmethod
    def validate_logging_level(cls, value: str) -> str:
        if value not in ("http", "https"):
            msg = 'Protocol must be "http" or "https".'
            raise ValueError(msg)
        return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
    )

    logging: int = 20
    app: App = App()
    db: None | Database = None
    redis: None | Redis = None
    email: None | Email = None
    token: Token
    superuser: Superuser = Superuser()

    @field_validator("logging", mode="before")
    @classmethod
    def validate_logging_level(cls, value: str | int) -> int:
        if isinstance(value, str):
            return getattr(logging, value)
        return value


settings = Settings()
