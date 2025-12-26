"""Configuration models using Pydantic"""

import os
from typing import Any

from pydantic import BaseModel, Field, field_validator


class BotConfig(BaseModel):
    """Telegram bot configuration"""

    token: str = Field(..., description="Telegram bot token")
    test_mode: bool = Field(default=False, description="Enable test mode")
    webhook_url: str | None = Field(default=None, description="Public URL for webhook")
    webhook_path: str = Field(default="/bot/webhook", description="Webhook endpoint path")

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

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: str | None) -> str | None:
        if v and v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            return os.getenv(env_var)
        return v


class ButtonConfig(BaseModel):
    """Configuration for inline keyboard button"""
    
    text: str = Field(..., description="Button text")
    url: str | None = Field(default=None, description="URL to open")
    callback_data: str | None = Field(default=None, description="Callback data")


class EndpointConfig(BaseModel):
    """Configuration for a single notification endpoint"""

    path: str = Field(..., description="API endpoint path")
    chat_id: str | None = Field(default=None, description="Telegram chat ID or username")
    chat_ids: list[str] = Field(default_factory=list, description="Multiple chat IDs")
    formatter: str = Field(default="plain", description="Formatter to use")
    template: str | None = Field(default=None, description="Template name to use")
    parse_mode: str | None = Field(default=None, description="Telegram parse mode")
    plugin_config: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict, description="Custom labels for keys")
    field_map: dict[str, str] = Field(default_factory=dict, description="Map payload fields to internal fields")
    buttons: list[list[ButtonConfig]] = Field(default_factory=list, description="Inline keyboard buttons (rows)")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v.startswith("/"):
            return f"/{v}"
        return v

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, v: str | None) -> str | None:
        if v is None:
            return v
        import logging
        logger = logging.getLogger(__name__)
        
        if v.startswith("@"):
            return v
        try:
            chat_id_int = int(v)
            if chat_id_int > 0 and len(v) > 10:
                logger.warning(f"chat_id '{v}' looks like a channel ID but is positive. Did you mean '-100{v}'?")
        except ValueError:
            logger.warning(f"chat_id '{v}' is not a valid numeric ID or @username")
        return v

    def get_chat_ids(self) -> list[str]:
        """Get all chat IDs (combines chat_id and chat_ids)"""
        ids = list(self.chat_ids)
        if self.chat_id:
            ids.insert(0, self.chat_id)
        return ids


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


class CallbackConfig(BaseModel):
    """Configuration for button callback handlers"""
    
    data: str = Field(..., description="Callback data to match")
    response: str | None = Field(default=None, description="Text response to send")
    url: str | None = Field(default=None, description="URL to POST callback to")


class CommandConfig(BaseModel):
    """Configuration for bot command handlers"""
    
    command: str = Field(..., description="Command to match (e.g., /start, /help)")
    response: str | None = Field(default=None, description="Text response (supports Jinja2)")
    parse_mode: str | None = Field(default=None, description="Parse mode for response")
    buttons: list[list[ButtonConfig]] = Field(default_factory=list, description="Optional buttons")


class AppConfig(BaseModel):
    """Root configuration model"""

    bot: BotConfig
    endpoints: list[EndpointConfig]
    templates: dict[str, str] = Field(default_factory=dict, description="Message templates")
    callbacks: list[CallbackConfig] = Field(default_factory=list, description="Button callback handlers")
    commands: list[CommandConfig] = Field(default_factory=list, description="Bot command handlers")
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
