"""Dynamic route registration for notification endpoints"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Header
from jinja2 import Template

from telenotif.core.config import EndpointConfig
from telenotif.core.interfaces import IPlugin
from telenotif.utils import escape_markdown_v2

logger = logging.getLogger(__name__)


def setup_routes(app: FastAPI) -> None:
    """Setup dynamic routes based on configuration"""
    config = app.state.config
    bot = app.state.bot
    registry = app.state.registry
    templates = app.state.templates

    for endpoint_config in config.endpoints:
        create_endpoint_handler(app, endpoint_config, bot, registry, config.server.api_key, templates)


def create_endpoint_handler(
    app: FastAPI,
    endpoint_config: EndpointConfig,
    bot,
    registry,
    api_key: str | None,
    templates: dict[str, str],
) -> None:
    """Create handler for a specific endpoint"""

    def get_field(payload: dict, field: str, default=None):
        """Get field value using field_map or direct access"""
        mapped = endpoint_config.field_map.get(field)
        if mapped:
            # Support nested fields with dot notation
            value = payload
            for key in mapped.split("."):
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return default
            return value if value is not None else default
        return payload.get(field, default)

    def render_template(template_str: str, payload: dict, parse_mode: str | None) -> str:
        """Render Jinja2 template with payload values"""
        def escape_value(v):
            if isinstance(v, list):
                return [escape_markdown_v2(str(i)) if not isinstance(i, (dict, list)) else i for i in v]
            if isinstance(v, dict):
                return {k: escape_value(val) for k, val in v.items()}
            return escape_markdown_v2(str(v))

        if parse_mode == "MarkdownV2":
            escaped_payload = {k: escape_value(v) for k, v in payload.items()}
            return Template(template_str).render(**escaped_payload)
        return Template(template_str).render(**payload)

    async def handler(
        payload: dict[str, Any],
        x_api_key: str | None = Header(None),
    ):
        if api_key and x_api_key != api_key:
            raise HTTPException(status_code=401, detail={"error": "invalid_api_key", "message": "Invalid or missing API key"})

        try:
            chat_id = get_field(payload, "chat_id") or endpoint_config.chat_id

            # Use template if specified, otherwise use formatter
            if endpoint_config.template and endpoint_config.template in templates:
                formatted_message = render_template(templates[endpoint_config.template], payload, parse_mode)
            else:
                formatter = registry.get_formatter(endpoint_config.formatter)
                if not formatter:
                    raise HTTPException(
                        status_code=500,
                        detail={"error": "formatter_not_found", "message": f"Formatter '{endpoint_config.formatter}' not found"},
                    )

                # Set labels if formatter supports it
                if hasattr(formatter, "labels"):
                    formatter.labels = endpoint_config.labels

                if isinstance(formatter, IPlugin):
                    formatted_message = formatter.format(payload, endpoint_config.plugin_config)
                else:
                    formatted_message = formatter.format(payload)

            parse_mode = get_field(payload, "parse_mode") or endpoint_config.parse_mode

            # Send to Telegram
            image_url = get_field(payload, "image_url")
            image_urls = get_field(payload, "image_urls", [])

            if image_urls:
                result = await bot.send_media_group(
                    chat_id=chat_id,
                    photo_urls=image_urls,
                    caption=formatted_message,
                    parse_mode=parse_mode,
                )
            elif image_url:
                result = await bot.send_photo(
                    chat_id=chat_id,
                    photo_url=image_url,
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
                "message_id": result.get("result", {}).get("message_id") if isinstance(result.get("result"), dict) else result.get("result", [{}])[0].get("message_id"),
                "chat_id": chat_id,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to send notification: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail={"error": "send_failed", "message": str(e)})

    app.post(endpoint_config.path)(handler)
    logger.info(f"Registered endpoint: {endpoint_config.path}")
