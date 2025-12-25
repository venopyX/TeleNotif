"""FastAPI application factory"""

import logging
from pathlib import Path

import yaml
from fastapi import FastAPI

from telenotif.core.bot import TelegramBot
from telenotif.core.config import AppConfig
from telenotif.core.registry import PluginRegistry
from telenotif.formatters import MarkdownFormatter, PlainFormatter
from telenotif.server.routes import setup_routes

logger = logging.getLogger(__name__)


def create_app(config_path: str = "config.yaml") -> FastAPI:
    """Create and configure FastAPI application"""
    config = load_config(config_path)

    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
    )

    app = FastAPI(
        title="TeleNotif",
        description="Simple Telegram notification framework",
        version="1.0.0",
    )

    bot = TelegramBot(token=config.bot.token, test_mode=config.bot.test_mode)

    registry = PluginRegistry()
    registry.register_formatter("plain", PlainFormatter())
    registry.register_formatter("markdown", MarkdownFormatter())

    plugins_dir = Path.cwd() / "plugins"
    if plugins_dir.exists():
        logger.info("Discovering plugins...")
        registry.discover_plugins(str(plugins_dir))
        logger.info(f"Loaded formatters: {', '.join(registry.list_formatters())}")

    app.state.config = config
    app.state.bot = bot
    app.state.registry = registry

    setup_routes(app)

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "endpoints": len(config.endpoints),
            "formatters": registry.list_formatters(),
        }

    logger.info(f"TeleNotif server initialized with {len(config.endpoints)} endpoints")

    return app


def load_config(config_path: str) -> AppConfig:
    """Load and validate configuration from YAML file"""
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_file) as f:
        config_data = yaml.safe_load(f)

    return AppConfig(**config_data)
