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
    template: str | None = Field(default=None, description="Template name to use")
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

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, v: str) -> str:
        import logging
        logger = logging.getLogger(__name__)
        
        if v.startswith("@"):
            return v
        try:
            chat_id_int = int(v)
            # Warn if looks like channel/supergroup but missing -100 prefix
            if chat_id_int > 0 and len(v) > 10:
                logger.warning(f"chat_id '{v}' looks like a channel ID but is positive. Did you mean '-100{v}'?")
        except ValueError:
            logger.warning(f"chat_id '{v}' is not a valid numeric ID or @username")
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
    templates: dict[str, str] = Field(default_factory=dict, description="Message templates")
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
