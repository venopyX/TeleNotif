"""Dynamic route registration for notification endpoints"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Header

from telenotif.core.config import EndpointConfig
from telenotif.core.interfaces import IPlugin

logger = logging.getLogger(__name__)


def setup_routes(app: FastAPI) -> None:
    """Setup dynamic routes based on configuration"""
    config = app.state.config
    bot = app.state.bot
    registry = app.state.registry

    for endpoint_config in config.endpoints:
        create_endpoint_handler(app, endpoint_config, bot, registry, config.server.api_key)


def create_endpoint_handler(
    app: FastAPI,
    endpoint_config: EndpointConfig,
    bot,
    registry,
    api_key: str | None,
) -> None:
    """Create handler for a specific endpoint"""

    async def handler(
        payload: dict[str, Any],
        x_api_key: str | None = Header(None),
    ):
        if api_key and x_api_key != api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")

        try:
            chat_id = payload.get("chat_id") or endpoint_config.chat_id

            formatter = registry.get_formatter(endpoint_config.formatter)
            if not formatter:
                raise HTTPException(
                    status_code=500,
                    detail=f"Formatter '{endpoint_config.formatter}' not found",
                )

            if isinstance(formatter, IPlugin):
                formatted_message = formatter.format(payload, endpoint_config.plugin_config)
            else:
                formatted_message = formatter.format(payload)

            parse_mode = payload.get("parse_mode") or endpoint_config.parse_mode

            if payload.get("image_url"):
                result = await bot.send_photo(
                    chat_id=chat_id,
                    photo_url=payload["image_url"],
                    caption=formatted_message,
                    parse_mode=parse_mode,
                )
            else:
                result = await bot.send_message(
                    chat_id=chat_id,
                    text=formatted_message,
                    parse_mode=parse_mode,
                )

            logger.info(f"Notification sent to {chat_id}")

            return {
                "status": "sent",
                "message_id": result.get("result", {}).get("message_id"),
                "chat_id": chat_id,
            }

        except Exception as e:
            logger.error(f"Failed to send notification: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    app.post(endpoint_config.path)(handler)
    logger.info(f"Registered endpoint: {endpoint_config.path}")
