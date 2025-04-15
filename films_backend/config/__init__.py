import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_MODEL_CONFIG = SettingsConfigDict(
    alias_generator=lambda field_name: field_name.upper(),
    env_file='.env' if os.path.exists('.env') else None,
)


class AppConfig(BaseSettings):
    model_config = CONFIG_MODEL_CONFIG

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str

    secret_key: str
    jwt_ttl: int

    proxy: str

    yandex_redirect_uri: str
    client_secret: str
    client_id: str
    api_key_1: str
    api_key_2: str

    max_vote_rounds: int
    round_time: int
    round_timeout: int
    room_ttl: int

    redis_host: str
    redis_port: int


app_config = AppConfig()
