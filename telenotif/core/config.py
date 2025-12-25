"""Configuration models using Pydantic"""

import os
from typing import Any

from pydantic import BaseModel, Field, field_validator


class BotConfig(BaseModel):
    """Telegram bot configuration"""

    token: str = Field(..., description="Telegram bot token")
    test_mode: bool = Field(default=False, description="Enable test mode")

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            token = os.getenv(env_var)
            if not token:
                raise ValueError(f"Environment variable {env_var} not set")
            return token
        return v


class EndpointConfig(BaseModel):
    """Configuration for a single notification endpoint"""

    path: str = Field(..., description="API endpoint path")
    chat_id: str = Field(..., description="Telegram chat ID or username")
    formatter: str = Field(default="plain", description="Formatter to use")
    parse_mode: str | None = Field(default=None, description="Telegram parse mode")
    plugin_config: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict, description="Custom labels for keys")
    field_map: dict[str, str] = Field(default_factory=dict, description="Map payload fields to internal fields")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v.startswith("/"):
            return f"/{v}"
        return v


class ServerConfig(BaseModel):
    """Server configuration"""

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    api_key: str | None = Field(default=None, description="API key for authentication")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str | None) -> str | None:
        if v and v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            return os.getenv(env_var)
        return v


class LoggingConfig(BaseModel):
    """Logging configuration"""

    level: str = Field(default="INFO", description="Log level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )


class AppConfig(BaseModel):
    """Root configuration model"""

    bot: BotConfig
    endpoints: list[EndpointConfig]
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
