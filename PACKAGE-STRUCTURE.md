"""
TeleNotif - Simple Telegram Notification Framework
Complete directory structure and core files
"""

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================

"""
telenotif/                          # Root package directory
├── pyproject.toml                  # Poetry/pip configuration
├── README.md                       # Package documentation
├── LICENSE                         # MIT License
├── .gitignore                      # Git ignore file
│
├── telenotif/                      # Main package
│   ├── __init__.py                 # Package exports
│   ├── __version__.py              # Version info
│   │
│   ├── core/                       # Core functionality
│   │   ├── __init__.py
│   │   ├── interfaces.py           # Abstract base classes
│   │   ├── registry.py             # Plugin discovery & registration
│   │   ├── config.py               # Configuration models (Pydantic)
│   │   └── bot.py                  # Telegram bot sender
│   │
│   ├── formatters/                 # Built-in formatters
│   │   ├── __init__.py
│   │   ├── base.py                 # Base formatter
│   │   ├── plain.py                # Plain text formatter
│   │   └── markdown.py             # Markdown formatter
│   │
│   ├── server/                     # FastAPI server
│   │   ├── __init__.py
│   │   ├── app.py                  # App factory
│   │   └── routes.py               # Dynamic route handler
│   │
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py
│   │   └── commands.py             # CLI commands
│   │
│   └── utils/                      # Utilities
│       ├── __init__.py
│       └── validators.py           # Payload validators
│
├── templates/                      # Project templates (for `init` command)
│   ├── config.yaml.template
│   ├── main.py.template
│   ├── README.md.template
│   └── plugins/
│       └── example_formatter.py.template
│
└── tests/                          # Test suite
    ├── __init__.py
    ├── conftest.py                 # Pytest fixtures
    ├── test_config.py
    ├── test_registry.py
    ├── test_bot.py
    ├── test_formatters.py
    └── test_server.py
"""

# ============================================================================
# FILE: pyproject.toml
# ============================================================================

PYPROJECT_TOML = """
[tool.poetry]
name = "telenotif"
version = "1.0.0"
description = "Simple Telegram notification framework with plugin support"
authors = ["Your Name <you@example.com>"]
license = "MIT"
readme = "README.md"
homepage = "https://github.com/yourusername/telenotif"
repository = "https://github.com/yourusername/telenotif"
keywords = ["telegram", "notifications", "bot", "webhook"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.104.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
aiohttp = "^3.9.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pyyaml = "^6.0"
click = "^8.1.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
black = "^23.11.0"
ruff = "^0.1.6"
mypy = "^1.7.0"

[tool.poetry.scripts]
telenotif = "telenotif.cli.commands:cli"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
"""

# ============================================================================
# FILE: telenotif/__init__.py
# ============================================================================

INIT_PY = """
\"\"\"TeleNotif - Simple Telegram Notification Framework\"\"\"

from telenotif.__version__ import __version__
from telenotif.server.app import create_app
from telenotif.core.interfaces import IFormatter, IPlugin

__all__ = [
    "__version__",
    "create_app",
    "IFormatter",
    "IPlugin",
]
"""

# ============================================================================
# FILE: telenotif/__version__.py
# ============================================================================

VERSION_PY = """
\"\"\"Version information\"\"\"

__version__ = "1.0.0"
"""

# ============================================================================
# FILE: telenotif/core/interfaces.py
# ============================================================================

INTERFACES_PY = """
\"\"\"Core interfaces for TeleNotif plugin system\"\"\"

from abc import ABC, abstractmethod
from typing import Any, Dict


class IFormatter(ABC):
    \"\"\"Interface for message formatters\"\"\"

    @abstractmethod
    def format(self, payload: Dict[str, Any]) -> str:
        \"\"\"
        Format payload into message string
        
        Args:
            payload: Dictionary containing message data
            
        Returns:
            Formatted message string
        \"\"\"
        pass


class IPlugin(ABC):
    \"\"\"Interface for custom plugins with configuration support\"\"\"

    @property
    @abstractmethod
    def name(self) -> str:
        \"\"\"
        Unique plugin identifier
        
        Returns:
            Plugin name (matches config)
        \"\"\"
        pass

    @abstractmethod
    def format(self, payload: Dict[str, Any], config: Dict[str, Any]) -> str:
        \"\"\"
        Format payload with plugin-specific configuration
        
        Args:
            payload: Dictionary containing message data
            config: Plugin-specific configuration from YAML
            
        Returns:
            Formatted message string
        \"\"\"
        pass
"""

# ============================================================================
# FILE: telenotif/core/config.py
# ============================================================================

CONFIG_PY = """
\"\"\"Configuration models using Pydantic\"\"\"

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import os


class BotConfig(BaseModel):
    \"\"\"Telegram bot configuration\"\"\"
    
    token: str = Field(..., description="Telegram bot token")
    test_mode: bool = Field(default=False, description="Enable test mode (log instead of send)")
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        # Support environment variable substitution
        if v.startswith('${') and v.endswith('}'):
            env_var = v[2:-1]
            token = os.getenv(env_var)
            if not token:
                raise ValueError(f"Environment variable {env_var} not set")
            return token
        return v


class EndpointConfig(BaseModel):
    \"\"\"Configuration for a single notification endpoint\"\"\"
    
    path: str = Field(..., description="API endpoint path (e.g., /notify/orders)")
    chat_id: str = Field(..., description="Telegram chat ID or username")
    formatter: str = Field(default="plain", description="Formatter to use")
    parse_mode: Optional[str] = Field(default=None, description="Telegram parse mode")
    plugin_config: Dict[str, Any] = Field(default_factory=dict, description="Plugin-specific config")
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v.startswith('/'):
            return f"/{v}"
        return v


class ServerConfig(BaseModel):
    \"\"\"Server configuration\"\"\"
    
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: Optional[str]) -> Optional[str]:
        if v and v.startswith('${') and v.endswith('}'):
            env_var = v[2:-1]
            return os.getenv(env_var)
        return v


class LoggingConfig(BaseModel):
    \"\"\"Logging configuration\"\"\"
    
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )


class AppConfig(BaseModel):
    \"\"\"Root configuration model\"\"\"
    
    bot: BotConfig
    endpoints: List[EndpointConfig]
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
"""

# ============================================================================
# FILE: .gitignore
# ============================================================================

GITIGNORE = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Config
.env
config.local.yaml
"""

# ============================================================================
# FILE: README.md
# ============================================================================

README_MD = """
# TeleNotif

> Simple Telegram notification framework with plugin support

## Installation

```bash
pip install telenotif
```

## Quick Start

### 1. Create a new project

```bash
telenotif init my_notifier
cd my_notifier
```

### 2. Configure your bot

Edit `config.yaml`:

```yaml
bot:
  token: "${TELEGRAM_BOT_TOKEN}"

endpoints:
  - path: "/notify/orders"
    chat_id: "-1001234567890"
    formatter: "plain"
```

### 3. Run the server

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
telenotif run
```

### 4. Send a notification

```bash
curl -X POST http://localhost:8000/notify/orders \\
  -H "Content-Type: application/json" \\
  -d '{"message": "New order received!", "order_id": 123}'
```

## Features

- 🚀 **Simple**: Install, configure, run
- 🔌 **Plugin-based**: Custom formatters without touching core
- 📱 **Telegram-native**: Supports all chat types (private, groups, channels)
- 🎨 **Flexible formatting**: Plain text, Markdown, or custom plugins
- 🔒 **Secure**: API key authentication
- 🐳 **Docker-ready**: Easy deployment

## Configuration

See [documentation](https://github.com/yourusername/telenotif) for full configuration options.

## Custom Plugins

Create `plugins/my_formatter.py`:

```python
from telenotif import IPlugin

class MyFormatter(IPlugin):
    @property
    def name(self):
        return "my_formatter"
    
    def format(self, payload, config):
        return f"{config['prefix']}: {payload['message']}"
```

## License

MIT License - see LICENSE file for details
"""

# ============================================================================
# FILE: telenotif/core/registry.py
# ============================================================================

REGISTRY_PY = """
\"\"\"Plugin registry for discovering and managing formatters and plugins\"\"\"

import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union

from telenotif.core.interfaces import IFormatter, IPlugin


class PluginRegistry:
    \"\"\"Registry for managing formatters and plugins\"\"\"

    def __init__(self):
        self._formatters: Dict[str, Union[IFormatter, IPlugin]] = {}

    def register_formatter(self, name: str, formatter: Union[IFormatter, IPlugin]) -> None:
        \"\"\"Register a formatter or plugin\"\"\"
        self._formatters[name] = formatter

    def get_formatter(self, name: str) -> Optional[Union[IFormatter, IPlugin]]:
        \"\"\"Get formatter by name\"\"\"
        return self._formatters.get(name)

    def discover_plugins(self, plugins_dir: str = "plugins") -> None:
        \"\"\"
        Auto-discover plugins from plugins directory
        
        Scans the plugins directory for Python files and imports classes
        that inherit from IFormatter or IPlugin
        \"\"\"
        plugins_path = Path(plugins_dir)
        
        if not plugins_path.exists():
            return

        # Add plugins directory to Python path
        if str(plugins_path.parent) not in sys.path:
            sys.path.insert(0, str(plugins_path.parent))

        # Scan for Python files
        for file_path in plugins_path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            module_name = f"{plugins_path.name}.{file_path.stem}"
            
            try:
                module = importlib.import_module(module_name)
                
                # Find classes that implement IFormatter or IPlugin
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj in (IFormatter, IPlugin):
                        continue
                        
                    if issubclass(obj, (IFormatter, IPlugin)):
                        instance = obj()
                        
                        # Get plugin name
                        if hasattr(instance, 'name'):
                            plugin_name = instance.name
                        else:
                            plugin_name = name.lower()
                        
                        self.register_formatter(plugin_name, instance)
                        
            except Exception as e:
                print(f"Warning: Failed to load plugin from {file_path}: {e}")

    def list_formatters(self) -> list[str]:
        \"\"\"List all registered formatters\"\"\"
        return list(self._formatters.keys())


# Global registry instance
registry = PluginRegistry()
"""

# ============================================================================
# FILE: telenotif/core/bot.py
# ============================================================================

BOT_PY = """
\"\"\"Telegram bot sender with retry logic\"\"\"

import asyncio
import logging
from typing import Optional
from urllib.parse import urljoin

import aiohttp


logger = logging.getLogger(__name__)


class TelegramBot:
    \"\"\"Telegram bot for sending messages\"\"\"

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, token: str, test_mode: bool = False):
        self.token = token
        self.test_mode = test_mode
        self.base_url = f"{self.BASE_URL}{token}/"

    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        max_retries: int = 3,
    ) -> dict:
        \"\"\"
        Send text message to Telegram
        
        Args:
            chat_id: Target chat ID or username
            text: Message text
            parse_mode: Parse mode (Markdown, HTML, or None)
            max_retries: Maximum retry attempts
            
        Returns:
            Response from Telegram API
        \"\"\"
        if self.test_mode:
            logger.info(f"TEST MODE - Would send to {chat_id}: {text}")
            return {"ok": True, "result": {"message_id": 0}}

        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode

        return await self._send_with_retry("sendMessage", payload, max_retries)

    async def send_photo(
        self,
        chat_id: str,
        photo_url: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        max_retries: int = 3,
    ) -> dict:
        \"\"\"
        Send photo to Telegram
        
        Args:
            chat_id: Target chat ID or username
            photo_url: URL of the photo
            caption: Optional caption
            parse_mode: Parse mode for caption
            max_retries: Maximum retry attempts
            
        Returns:
            Response from Telegram API
        \"\"\"
        if self.test_mode:
            logger.info(f"TEST MODE - Would send photo to {chat_id}: {photo_url}")
            return {"ok": True, "result": {"message_id": 0}}

        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
        }
        
        if caption:
            payload["caption"] = caption
        if parse_mode:
            payload["parse_mode"] = parse_mode

        return await self._send_with_retry("sendPhoto", payload, max_retries)

    async def _send_with_retry(
        self, method: str, payload: dict, max_retries: int
    ) -> dict:
        \"\"\"Send request with exponential backoff retry\"\"\"
        url = urljoin(self.base_url, method)
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        result = await response.json()
                        
                        if response.status == 200:
                            return result
                        
                        # Handle rate limiting
                        if response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", 1))
                            logger.warning(f"Rate limited. Retrying after {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        # Handle other errors
                        error_msg = result.get("description", "Unknown error")
                        logger.error(f"Telegram API error: {error_msg}")
                        
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt
                            logger.info(f"Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                        else:
                            raise Exception(f"Failed after {max_retries} attempts: {error_msg}")
                            
            except aiohttp.ClientError as e:
                logger.error(f"Network error: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise

        raise Exception(f"Failed to send message after {max_retries} attempts")
"""

# ============================================================================
# FILE: telenotif/formatters/base.py
# ============================================================================

FORMATTERS_BASE_PY = """
\"\"\"Base formatter implementation\"\"\"

from typing import Any, Dict

from telenotif.core.interfaces import IFormatter


class BaseFormatter(IFormatter):
    \"\"\"Base class for formatters providing common functionality\"\"\"

    def format(self, payload: Dict[str, Any]) -> str:
        \"\"\"Default implementation - override in subclasses\"\"\"
        return self._dict_to_string(payload)

    def _dict_to_string(self, data: Dict[str, Any], indent: int = 0) -> str:
        \"\"\"Convert dictionary to readable string format\"\"\"
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{' ' * indent}{key}:")
                lines.append(self._dict_to_string(value, indent + 2))
            elif isinstance(value, list):
                lines.append(f"{' ' * indent}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(self._dict_to_string(item, indent + 2))
                    else:
                        lines.append(f"{' ' * (indent + 2)}- {item}")
            else:
                lines.append(f"{' ' * indent}{key}: {value}")
        return "\\n".join(lines)
"""

# ============================================================================
# FILE: telenotif/formatters/plain.py
# ============================================================================

FORMATTERS_PLAIN_PY = """
\"\"\"Plain text formatter\"\"\"

from typing import Any, Dict

from telenotif.formatters.base import BaseFormatter


class PlainFormatter(BaseFormatter):
    \"\"\"
    Plain text formatter - converts payload to simple key: value format
    
    Example:
        Input: {"message": "Hello", "user": "John"}
        Output: "message: Hello\\nuser: John"
    \"\"\"

    def format(self, payload: Dict[str, Any]) -> str:
        # If there's a 'message' key, prioritize it
        if "message" in payload and len(payload) == 1:
            return str(payload["message"])
        
        return self._dict_to_string(payload)
"""

# ============================================================================
# FILE: telenotif/formatters/markdown.py
# ============================================================================

FORMATTERS_MARKDOWN_PY = """
\"\"\"Markdown formatter for Telegram\"\"\"

from typing import Any, Dict

from telenotif.formatters.base import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    \"\"\"
    Markdown formatter - converts payload to Telegram Markdown format
    
    Example:
        Input: {"title": "Alert", "details": "CPU > 90%"}
        Output: "*Alert*\\nDetails: CPU > 90%"
    \"\"\"

    def format(self, payload: Dict[str, Any]) -> str:
        lines = []
        
        for key, value in payload.items():
            if key.lower() in ["title", "heading", "header"]:
                lines.append(f"*{value}*")
            elif isinstance(value, dict):
                lines.append(f"*{key}:*")
                lines.append(self._format_nested(value))
            elif isinstance(value, list):
                lines.append(f"*{key}:*")
                for item in value:
                    lines.append(f"  • {item}")
            else:
                lines.append(f"{key}: {value}")
        
        return "\\n".join(lines)

    def _format_nested(self, data: Dict[str, Any], indent: str = "  ") -> str:
        \"\"\"Format nested dictionary with indentation\"\"\"
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{indent}{key}: {value}")
            else:
                lines.append(f"{indent}{key}: {value}")
        return "\\n".join(lines)
"""

# ============================================================================
# FILE: telenotif/formatters/__init__.py
# ============================================================================

FORMATTERS_INIT_PY = """
\"\"\"Built-in formatters\"\"\"

from telenotif.formatters.plain import PlainFormatter
from telenotif.formatters.markdown import MarkdownFormatter

__all__ = ["PlainFormatter", "MarkdownFormatter"]
"""

# ============================================================================
# FILE: telenotif/server/app.py
# ============================================================================

SERVER_APP_PY = """
\"\"\"FastAPI application factory\"\"\"

import logging
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI

from telenotif.core.bot import TelegramBot
from telenotif.core.config import AppConfig
from telenotif.core.registry import PluginRegistry
from telenotif.formatters import MarkdownFormatter, PlainFormatter
from telenotif.server.routes import setup_routes


logger = logging.getLogger(__name__)


def create_app(config_path: str = "config.yaml") -> FastAPI:
    \"\"\"
    Create and configure FastAPI application
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Configured FastAPI application
    \"\"\"
    # Load configuration
    config = load_config(config_path)
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
    )
    
    # Create FastAPI app
    app = FastAPI(
        title="TeleNotif",
        description="Simple Telegram notification framework",
        version="1.0.0",
    )
    
    # Create Telegram bot
    bot = TelegramBot(token=config.bot.token, test_mode=config.bot.test_mode)
    
    # Create plugin registry
    registry = PluginRegistry()
    
    # Register built-in formatters
    registry.register_formatter("plain", PlainFormatter())
    registry.register_formatter("markdown", MarkdownFormatter())
    
    # Discover user plugins
    plugins_dir = Path.cwd() / "plugins"
    if plugins_dir.exists():
        logger.info("Discovering plugins...")
        registry.discover_plugins(str(plugins_dir))
        logger.info(f"Loaded formatters: {', '.join(registry.list_formatters())}")
    
    # Store in app state
    app.state.config = config
    app.state.bot = bot
    app.state.registry = registry
    
    # Setup routes
    setup_routes(app)
    
    # Health check endpoint
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
    \"\"\"Load and validate configuration from YAML file\"\"\"
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file) as f:
        config_data = yaml.safe_load(f)
    
    return AppConfig(**config_data)
"""

# ============================================================================
# FILE: telenotif/server/routes.py
# ============================================================================

SERVER_ROUTES_PY = """
\"\"\"Dynamic route registration for notification endpoints\"\"\"

import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel, Field

from telenotif.core.config import EndpointConfig
from telenotif.core.interfaces import IPlugin


logger = logging.getLogger(__name__)


class NotificationPayload(BaseModel):
    \"\"\"Base notification payload\"\"\"
    
    message: str = Field(..., description="Message text")
    image_url: Optional[str] = Field(None, description="Optional image URL")
    parse_mode: Optional[str] = Field(None, description="Parse mode override")
    chat_id: Optional[str] = Field(None, description="Chat ID override")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional data")

    class Config:
        extra = "allow"  # Allow additional fields


def setup_routes(app: FastAPI) -> None:
    \"\"\"
    Setup dynamic routes based on configuration
    
    Creates a POST endpoint for each configured notification endpoint
    \"\"\"
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
    api_key: Optional[str],
) -> None:
    \"\"\"Create handler for a specific endpoint\"\"\"
    
    async def handler(
        request: Request,
        payload: Dict[str, Any],
        x_api_key: Optional[str] = Header(None),
    ):
        # Authentication
        if api_key and x_api_key != api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        try:
            # Parse payload
            notif = NotificationPayload(**payload)
            
            # Determine chat ID
            chat_id = notif.chat_id or endpoint_config.chat_id
            
            # Get formatter
            formatter = registry.get_formatter(endpoint_config.formatter)
            if not formatter:
                raise HTTPException(
                    status_code=500,
                    detail=f"Formatter '{endpoint_config.formatter}' not found"
                )
            
            # Format message
            if isinstance(formatter, IPlugin):
                # Plugin with config support
                formatted_message = formatter.format(payload, endpoint_config.plugin_config)
            else:
                # Simple formatter
                formatted_message = formatter.format(payload)
            
            # Determine parse mode
            parse_mode = notif.parse_mode or endpoint_config.parse_mode
            
            # Send to Telegram
            if notif.image_url:
                result = await bot.send_photo(
                    chat_id=chat_id,
                    photo_url=notif.image_url,
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
    
    # Register route
    app.post(endpoint_config.path)(handler)
    logger.info(f"Registered endpoint: {endpoint_config.path}")
"""

# ============================================================================
# FILE: telenotif/server/__init__.py
# ============================================================================

SERVER_INIT_PY = """
\"\"\"FastAPI server components\"\"\"

from telenotif.server.app import create_app

__all__ = ["create_app"]
"""

# ============================================================================
# FILE: telenotif/cli/commands.py
# ============================================================================

CLI_COMMANDS_PY = """
\"\"\"Command-line interface for TeleNotif\"\"\"

import os
import shutil
from pathlib import Path

import click
import uvicorn
import yaml


@click.group()
@click.version_option(version="1.0.0")
def cli():
    \"\"\"TeleNotif - Simple Telegram Notification Framework\"\"\"
    pass


@cli.command()
@click.argument("project_name")
def init(project_name: str):
    \"\"\"
    Initialize a new TeleNotif project
    
    Creates directory structure and configuration templates
    \"\"\"
    project_path = Path(project_name)
    
    if project_path.exists():
        click.echo(f"Error: Directory '{project_name}' already exists", err=True)
        return
    
    click.echo(f"Creating project: {project_name}")
    
    # Create directories
    project_path.mkdir()
    (project_path / "plugins").mkdir()
    
    # Create config.yaml
    config_content = \"\"\"# TeleNotif Configuration

bot:
  token: "${TELEGRAM_BOT_TOKEN}"  # Set via environment variable
  test_mode: false                 # Set to true for testing without sending

# Define notification endpoints
endpoints:
  # Example: Order notifications
  - path: "/notify/orders"
    chat_id: "-1001234567890"     # Your channel/group ID
    formatter: "plain"             # plain, markdown, or custom plugin name
    parse_mode: null               # Optional: Markdown, HTML
    
  # Example: Alert notifications
  - path: "/notify/alerts"
    chat_id: "123456789"           # Private chat user ID
    formatter: "markdown"
    parse_mode: "Markdown"

# Server configuration
server:
  host: "0.0.0.0"
  port: 8000
  api_key: "${API_KEY}"            # Optional: Set for authentication

# Logging
logging:
  level: "INFO"                    # DEBUG, INFO, WARNING, ERROR
\"\"\"
    (project_path / "config.yaml").write_text(config_content)
    
    # Create main.py
    main_content = \"\"\"\"\"\"TeleNotif server entry point\"\"\"

from telenotif import create_app

if __name__ == "__main__":
    import uvicorn
    
    app = create_app("config.yaml")
    uvicorn.run(app, host="0.0.0.0", port=8000)
\"\"\"
    (project_path / "main.py").write_text(main_content)
    
    # Create example plugin
    plugin_content = \"\"\"\"\"\"Example custom formatter plugin\"\"\"

from typing import Any, Dict
from telenotif import IPlugin


class OrderFormatter(IPlugin):
    \"\"\"Custom formatter for order notifications\"\"\"
    
    @property
    def name(self) -> str:
        return "order_formatter"
    
    def format(self, payload: Dict[str, Any], config: Dict[str, Any]) -> str:
        \"\"\"Format order notification with custom styling\"\"\"
        prefix = config.get("prefix", "🛒 New Order")
        
        lines = [prefix, ""]
        
        if "order_id" in payload:
            lines.append(f"Order ID: #{payload['order_id']}")
        if "user" in payload:
            lines.append(f"Customer: {payload['user']}")
        if "items" in payload:
            lines.append(f"Items: {payload['items']}")
        if "total" in payload:
            lines.append(f"Total: ${payload['total']}")
        
        if "message" in payload:
            lines.append("")
            lines.append(payload["message"])
        
        return "\\n".join(lines)
\"\"\"
    (project_path / "plugins" / "example_formatter.py").write_text(plugin_content)
    
    # Create requirements.txt
    requirements = "telenotif>=1.0.0\\n"
    (project_path / "requirements.txt").write_text(requirements)
    
    # Create README
    readme = f\"\"\"# {project_name}

TeleNotif notification service

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your-bot-token"
   export API_KEY="your-secret-key"  # Optional
   ```

3. Edit `config.yaml` with your bot settings

4. Run the server:
   ```bash
   python main.py
   # or
   telenotif run
   ```

## Usage

Send a notification:

```bash
curl -X POST http://localhost:8000/notify/orders \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-secret-key" \\
  -d '{{"message": "New order received!", "order_id": 123}}'
```

## Custom Plugins

See `plugins/example_formatter.py` for plugin examples.
\"\"\"
    (project_path / "README.md").write_text(readme)
    
    # Create .env.example
    env_example = \"\"\"TELEGRAM_BOT_TOKEN=your_bot_token_here
API_KEY=your_api_key_here
\"\"\"
    (project_path / ".env.example").write_text(env_example)
    
    click.echo("✓ Project created successfully!")
    click.echo(f"\\nNext steps:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  # Edit config.yaml with your settings")
    click.echo(f"  export TELEGRAM_BOT_TOKEN='your-token'")
    click.echo(f"  telenotif run")


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
@click.option("--host", default=None, help="Override host")
@click.option("--port", default=None, type=int, help="Override port")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def run(config: str, host: str, port: int, reload: bool):
    \"\"\"
    Run the TeleNotif server
    \"\"\"
    if not Path(config).exists():
        click.echo(f"Error: Config file '{config}' not found", err=True)
        click.echo("Run 'telenotif init <project_name>' to create a new project")
        return
    
    # Load config to get default host/port
    with open(config) as f:
        config_data = yaml.safe_load(f)
    
    server_config = config_data.get("server", {})
    final_host = host or server_config.get("host", "0.0.0.0")
    final_port = port or server_config.get("port", 8000)
    
    click.echo(f"Starting TeleNotif server on {final_host}:{final_port}")
    click.echo(f"Config: {config}")
    
    if reload:
        click.echo("Auto-reload: enabled (development mode)")
    
    # Create app and run
    uvicorn.run(
        "telenotif.server.app:create_app",
        host=final_host,
        port=final_port,
        reload=reload,
        factory=True,
    )


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
def validate(config: str):
    \"\"\"
    Validate configuration file
    \"\"\"
    config_path = Path(config)
    
    if not config_path.exists():
        click.echo(f"Error: Config file '{config}' not found", err=True)
        return
    
    try:
        # Try to load config
        from telenotif.core.config import AppConfig
        
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        
        app_config = AppConfig(**config_data)
        
        click.echo("✓ Configuration is valid!")
        click.echo(f"\\nBot token: {'*' * 20}{app_config.bot.token[-4:]}")
        click.echo(f"Endpoints: {len(app_config.endpoints)}")
        
        for endpoint in app_config.endpoints:
            click.echo(f"  - {endpoint.path} → {endpoint.chat_id} ({endpoint.formatter})")
        
        # Check for plugins
        plugins_dir = Path.cwd() / "plugins"
        if plugins_dir.exists():
            plugins = [f.stem for f in plugins_dir.glob("*.py") if not f.name.startswith("_")]
            if plugins:
                click.echo(f"\\nPlugins found: {', '.join(plugins)}")
        
    except Exception as e:
        click.echo(f"✗ Configuration error: {e}", err=True)


@cli.command()
def list_formatters():
    \"\"\"
    List available formatters
    \"\"\"
    from telenotif.core.registry import PluginRegistry
    from telenotif.formatters import PlainFormatter, MarkdownFormatter
    
    registry = PluginRegistry()
    registry.register_formatter("plain", PlainFormatter())
    registry.register_formatter("markdown", MarkdownFormatter())
    
    # Load user plugins
    plugins_dir = Path.cwd() / "plugins"
    if plugins_dir.exists():
        registry.discover_plugins(str(plugins_dir))
    
    click.echo("Available formatters:")
    for name in registry.list_formatters():
        formatter = registry.get_formatter(name)
        click.echo(f"  • {name} - {formatter.__class__.__name__}")


if __name__ == "__main__":
    cli()
"""

# ============================================================================
# FILE: telenotif/cli/__init__.py
# ============================================================================

CLI_INIT_PY = """
\"\"\"CLI commands\"\"\"

from telenotif.cli.commands import cli

__all__ = ["cli"]
"""

# ============================================================================
# FILE: telenotif/utils/validators.py
# ============================================================================

VALIDATORS_PY = """
\"\"\"Validation utilities\"\"\"

import re
from typing import Any, Dict


def validate_chat_id(chat_id: str) -> bool:
    \"\"\"
    Validate Telegram chat ID format
    
    Valid formats:
    - User ID: positive integer (e.g., "123456789")
    - Group ID: negative integer (e.g., "-123456789")
    - Supergroup/Channel ID: starts with -100 (e.g., "-1001234567890")
    - Username: starts with @ (e.g., "@channel_name")
    \"\"\"
    # Username format
    if chat_id.startswith("@"):
        return len(chat_id) > 1 and chat_id[1:].replace("_", "").isalnum()
    
    # Numeric ID
    try:
        int(chat_id)
        return True
    except ValueError:
        return False


def validate_parse_mode(parse_mode: str) -> bool:
    \"\"\"Validate Telegram parse mode\"\"\"
    return parse_mode in ["Markdown", "MarkdownV2", "HTML"]


def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"Remove None values and empty strings from payload\"\"\"
    return {k: v for k, v in payload.items() if v is not None and v != ""}
"""

# ============================================================================
# FILE: telenotif/utils/__init__.py
# ============================================================================

UTILS_INIT_PY = """
\"\"\"Utility functions\"\"\"

from telenotif.utils.validators import validate_chat_id, validate_parse_mode, sanitize_payload

__all__ = ["validate_chat_id", "validate_parse_mode", "sanitize_payload"]
"""

# ============================================================================
# FILE: tests/conftest.py
# ============================================================================

TESTS_CONFTEST_PY = """
\"\"\"Pytest configuration and fixtures\"\"\"

import pytest
from pathlib import Path
import tempfile
import yaml


@pytest.fixture
def sample_config():
    \"\"\"Sample configuration dictionary\"\"\"
    return {
        "bot": {
            "token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "test_mode": True,
        },
        "endpoints": [
            {
                "path": "/notify/test",
                "chat_id": "123456789",
                "formatter": "plain",
            }
        ],
        "server": {
            "host": "0.0.0.0",
            "port": 8000,
        },
        "logging": {
            "level": "INFO",
        }
    }


@pytest.fixture
def config_file(sample_config):
    \"\"\"Create temporary config file\"\"\"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config, f)
        return f.name


@pytest.fixture
def mock_bot():
    \"\"\"Mock Telegram bot for testing\"\"\"
    from telenotif.core.bot import TelegramBot
    return TelegramBot(token="test_token", test_mode=True)
"""

# ============================================================================
# FILE: tests/test_config.py
# ============================================================================

TESTS_CONFIG_PY = """
\"\"\"Tests for configuration loading and validation\"\"\"

import pytest
from telenotif.core.config import AppConfig, BotConfig, EndpointConfig


def test_bot_config_valid():
    \"\"\"Test valid bot configuration\"\"\"
    config = BotConfig(token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    assert config.token
    assert config.test_mode is False


def test_endpoint_config_path_normalization():
    \"\"\"Test path normalization adds leading slash\"\"\"
    config = EndpointConfig(path="notify/test", chat_id="123")
    assert config.path == "/notify/test"


def test_app_config_loading(sample_config):
    \"\"\"Test full configuration loading\"\"\"
    config = AppConfig(**sample_config)
    assert config.bot.token
    assert len(config.endpoints) == 1
    assert config.server.port == 8000
"""

# ============================================================================
# FILE: tests/test_formatters.py
# ============================================================================

TESTS_FORMATTERS_PY = """
\"\"\"Tests for formatters\"\"\"

import pytest
from telenotif.formatters.plain import PlainFormatter
from telenotif.formatters.markdown import MarkdownFormatter


def test_plain_formatter_simple_message():
    \"\"\"Test plain formatter with simple message\"\"\"
    formatter = PlainFormatter()
    result = formatter.format({"message": "Hello World"})
    assert result == "Hello World"


def test_plain_formatter_dict():
    \"\"\"Test plain formatter with dictionary\"\"\"
    formatter = PlainFormatter()
    result = formatter.format({"user": "John", "status": "active"})
    assert "user: John" in result
    assert "status: active" in result


def test_markdown_formatter():
    \"\"\"Test markdown formatter\"\"\"
    formatter = MarkdownFormatter()
    result = formatter.format({"title": "Alert", "message": "Test"})
    assert "*Alert*" in result
"""

# ============================================================================
# FILE: tests/test_registry.py
# ============================================================================

TESTS_REGISTRY_PY = """
\"\"\"Tests for plugin registry\"\"\"

import pytest
from telenotif.core.registry import PluginRegistry
from telenotif.formatters.plain import PlainFormatter


def test_register_and_get_formatter():
    \"\"\"Test formatter registration and retrieval\"\"\"
    registry = PluginRegistry()
    formatter = PlainFormatter()
    
    registry.register_formatter("test", formatter)
    retrieved = registry.get_formatter("test")
    
    assert retrieved is formatter


def test_list_formatters():
    \"\"\"Test listing all formatters\"\"\"
    registry = PluginRegistry()
    registry.register_formatter("plain", PlainFormatter())
    registry.register_formatter("custom", PlainFormatter())
    
    formatters = registry.list_formatters()
    assert "plain" in formatters
    assert "custom" in formatters
    assert len(formatters) == 2
"""

# ============================================================================
# FILE: tests/test_bot.py
# ============================================================================

TESTS_BOT_PY = """
\"\"\"Tests for Telegram bot\"\"\"

import pytest
from telenotif.core.bot import TelegramBot


@pytest.mark.asyncio
async def test_bot_test_mode():
    \"\"\"Test bot in test mode (no actual sending)\"\"\"
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_message(chat_id="123", text="Test message")
    
    assert result["ok"] is True
    assert "result" in result


@pytest.mark.asyncio
async def test_bot_send_photo_test_mode():
    \"\"\"Test sending photo in test mode\"\"\"
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_photo(
        chat_id="123",
        photo_url="https://example.com/photo.jpg",
        caption="Test"
    )
    
    assert result["ok"] is True
"""

# ============================================================================
# FILE: LICENSE
# ============================================================================

LICENSE = """MIT License

Copyright (c) 2024 TeleNotif Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

print("✓ Complete implementation finished!")
print("\\n" + "="*60)
print("TELENOTIF PACKAGE STRUCTURE COMPLETE")
print("="*60)
print("\\nAll files created:")
print("  ✓ Core interfaces and bot")
print("  ✓ Plugin registry system")
print("  ✓ Built-in formatters (plain, markdown)")
print("  ✓ FastAPI server with dynamic routes")
print("  ✓ CLI commands (init, run, validate)")
print("  ✓ Test suite")
print("  ✓ Documentation")
print("\\nNext steps to build the package:")
print("  1. Create the directory structure")
print("  2. Copy all code into respective files")
print("  3. Run: poetry install")
print("  4. Run: pytest")
print("  5. Run: poetry build")
print("  6. Run: poetry publish")
print("\\nUsage example:")
print("  $ pip install telenotif")
print("  $ telenotif init my_notifier")
print("  $ cd my_notifier")
print("  $ export TELEGRAM_BOT_TOKEN='your-token'")
print("  $ telenotif run")
