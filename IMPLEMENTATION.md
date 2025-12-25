# TeleNotif - Simple Telegram Notification Framework
## Implementation Plan

## Executive Summary

A **lightweight PyPI package** that does ONE thing well: receive HTTP requests and send formatted Telegram notifications. Users install `telenotif`, create a config file, optionally add custom plugins for message formatting, and run the server. That's it.

**Core Philosophy**:
- **Simple by default**: Install, configure, run (3 steps)
- **One responsibility**: HTTP → Telegram (nothing more)
- **Plugin-based customization**: Add endpoints and formats without touching core
- **No database, no templates, no overhead**: Pure request forwarding

---

## High-Level Architecture

```
User's Website/App
       ↓ (HTTP POST)
   TeleNotif Server (FastAPI)
       ↓ (validates & routes)
   Plugin System (optional formatting)
       ↓ (sends)
   Telegram Bot API
       ↓
   Users/Channels/Groups
```

**What it does**:
1. Receives POST requests at configured endpoints
2. Validates payload structure
3. Applies optional formatting (via plugins)
4. Sends to Telegram (text/images to any chat type)
5. Returns success/failure response

**What it doesn't do**:
- No database
- No job queues
- No templates (plain formatting only)
- No multi-channel support (Telegram only)
- No UI/dashboard

---

## Phase 1: Package Structure

### Core Package (`telenotif/`)

```
telenotif/
├── __init__.py                 # Package entry + version
├── core/
│   ├── __init__.py
│   ├── interfaces.py           # IPlugin, IFormatter (minimal)
│   ├── registry.py             # Plugin discovery
│   ├── config.py               # YAML config loader (Pydantic models)
│   └── bot.py                  # Telegram sender (with retries)
├── formatters/
│   ├── __init__.py
│   ├── base.py                 # BaseFormatter
│   ├── plain.py                # Plain text (default)
│   └── markdown.py             # Markdown formatting
├── server/
│   ├── __init__.py
│   ├── app.py                  # FastAPI app factory
│   └── routes.py               # Dynamic route registration
├── cli/
│   ├── __init__.py
│   └── commands.py             # `telenotif init`, `telenotif run`
└── utils/
    ├── __init__.py
    └── validators.py           # Payload validation helpers
```

### User Project Structure (Created by `telenotif init`)

```
my_project/
├── config.yaml                 # All configuration
├── plugins/                    # Optional custom plugins
│   ├── __init__.py
│   └── order_formatter.py      # Example: custom message format
├── main.py                     # Entry point: `python main.py`
└── requirements.txt            # Just: telenotif==1.0.0
```

---

## Phase 2: Configuration System

### Single YAML File (`config.yaml`)

```yaml
# Bot credentials
bot:
  token: "${TELEGRAM_BOT_TOKEN}"  # Supports env vars

# Endpoints configuration
endpoints:
  - path: "/notify/orders"
    chat_id: "-1001234567890"     # Channel/group ID
    formatter: "plain"             # or "markdown" or plugin name
    
  - path: "/notify/alerts"
    chat_id: "123456789"           # Private chat (user ID)
    formatter: "markdown"
    parse_mode: "Markdown"         # Telegram parse mode
    
  - path: "/notify/custom"
    chat_id: "@my_channel"         # Username (channels only)
    formatter: "order_formatter"   # Custom plugin
    plugin_config:                 # Plugin-specific settings
      prefix: "🛒 New Order"

# Optional: Global settings
server:
  host: "0.0.0.0"
  port: 8000
  api_key: "${API_KEY}"            # Simple auth

logging:
  level: "INFO"                    # DEBUG, INFO, WARNING, ERROR
```

### Configuration Loading (Pydantic)

**Models for type safety**:
- `BotConfig`: Bot token validation
- `EndpointConfig`: Path, chat_id, formatter
- `ServerConfig`: Host, port, auth
- `AppConfig`: Root model containing all configs

**Features**:
- Environment variable substitution (`${VAR}`)
- Validation on load (invalid config = clear error message)
- Hot-reload support (watch file changes in dev mode)

---

## Phase 3: Plugin System (Minimal)

### Plugin Interface

**Only TWO interfaces needed**:

1. **IFormatter** - Transform payload into message text
```python
# Signature only (no actual code in plan)
class IFormatter(ABC):
    @abstractmethod
    def format(self, payload: dict) -> str:
        """Convert payload dict to message string"""
        pass
```

2. **IPlugin** (Optional) - For advanced needs
```python
class IPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier (matches config)"""
        pass
    
    @abstractmethod
    def format(self, payload: dict, config: dict) -> str:
        """Format with plugin-specific config"""
        pass
```

### Built-in Formatters

**PlainFormatter** (default):
```python
# Just returns payload as-is or simple string conversion
# Input: {"message": "Hello", "user": "John"}
# Output: "message: Hello\nuser: John"
```

**MarkdownFormatter**:
```python
# Converts dict to Markdown format
# Input: {"title": "Alert", "details": "CPU > 90%"}
# Output: "*Alert*\nDetails: CPU > 90%"
```

### Plugin Discovery

**Auto-discovery from `plugins/` directory**:
1. Scan for Python files
2. Import classes inheriting from `IPlugin`
3. Register in global registry
4. Map to endpoint via config

**No entry points or complex loading** - just import Python modules

---

## Phase 4: Core Logic

### Telegram Bot Integration

**Single sender class**:
- Uses `aiohttp` (no heavy library dependencies)
- Direct API calls to `https://api.telegram.org/bot{token}/sendMessage`
- Supports:
  - Text messages (with parse_mode)
  - Photos (`sendPhoto`)
  - Documents (`sendDocument`)
  - All chat types (private, group, channel, supergroup)

**Retry logic**:
- 3 retries with exponential backoff (1s, 2s, 4s)
- Handles Telegram rate limits (429 errors)
- Circuit breaker for repeated failures (optional)

**Payload structure** (minimal):
```python
{
    "message": "Text content",           # Required
    "image_url": "https://...",          # Optional
    "parse_mode": "Markdown",            # Optional override
    "chat_id": "123456789"               # Optional override
}
```

### FastAPI Server

**Dynamic route registration**:
- Read `endpoints` from config
- Create POST handler for each path
- Inject dependencies (formatter, bot, chat_id)

**Request flow**:
```
1. POST /notify/orders
2. Validate API key (if configured)
3. Parse JSON body
4. Get formatter from registry
5. Format message
6. Send to Telegram
7. Return {"status": "sent", "message_id": 12345}
```

**Error handling**:
- 400: Invalid payload
- 401: Invalid API key
- 500: Telegram API failure
- Include error details in response

---

## Phase 5: Developer Experience

### CLI Commands

**`telenotif init <project_name>`**:
- Creates directory structure
- Generates sample `config.yaml`
- Creates example plugin
- Adds `main.py` entry point

**`telenotif run`**:
- Loads config from current directory
- Starts FastAPI server with uvicorn
- Hot-reload in development mode

**`telenotif validate`**:
- Checks config.yaml syntax
- Validates bot token
- Tests connectivity to Telegram API
- Lists discovered plugins

### Simple Entry Point (`main.py`)

```python
# User's main.py (auto-generated)
from telenotif import create_app

if __name__ == "__main__":
    import uvicorn
    app = create_app("config.yaml")
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Plugin Development

**Example custom plugin** (user creates this):
```python
# plugins/order_formatter.py
from telenotif.core.interfaces import IPlugin

class OrderFormatter(IPlugin):
    @property
    def name(self):
        return "order_formatter"
    
    def format(self, payload: dict, config: dict) -> str:
        prefix = config.get("prefix", "Order")
        return f"{prefix}\nUser: {payload['user']}\nItem: {payload['item']}"
```

**That's it** - no registration code, no decorators, just implement interface

---

## Phase 6: Production Features (Minimal)

### Authentication

**Simple API key**:
- Set in config: `api_key: "secret123"`
- Check header: `X-API-Key: secret123`
- Return 401 if missing/invalid

**No OAuth, no JWT** - keep it simple

### Logging

**Structured logs** (using Python's logging):
- Request received: endpoint, payload size
- Message sent: chat_id, message_id
- Errors: with full traceback

**Configurable levels**: DEBUG, INFO, WARNING, ERROR

### Metrics (Optional)

**Prometheus-compatible endpoint** (`/metrics`):
- Total requests per endpoint
- Success/failure counts
- Average response time

**Only if user enables in config** (default: off)

### Health Check

**GET `/health`**:
```json
{
    "status": "healthy",
    "bot_connected": true,
    "endpoints": 3,
    "plugins": 1
}
```

---

## Phase 7: Telegram Features

### Supported Chat Types

**All types via single `chat_id` field**:
- Private chat: User ID (`123456789`)
- Group: Group ID (`-987654321`)
- Supergroup: Supergroup ID (`-1001234567890`)
- Channel: Channel ID or username (`@my_channel`)

**Auto-detection** - no need to specify type in config

### Message Types

**Text messages**:
```json
{"message": "Hello World"}
```

**With formatting**:
```json
{
    "message": "*Bold* and _italic_",
    "parse_mode": "Markdown"
}
```

**Images**:
```json
{
    "message": "Check this image",
    "image_url": "https://example.com/image.jpg"
}
```

**Override chat_id** (per request):
```json
{
    "message": "Alert",
    "chat_id": "123456789"  # Send to different chat
}
```

### Telegram API Best Practices

- Respect rate limits (30 messages/second to same chat)
- Handle `Too Many Requests` (429) with retry
- Validate chat_id format before sending
- Support both bot token and user access token (future)

---

## Phase 8: Deployment

### PyPI Package

**Package metadata**:
```toml
[tool.poetry]
name = "telenotif"
version = "1.0.0"
description = "Simple Telegram notification framework"
authors = ["Your Name"]
license = "MIT"

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.104"
pydantic = "^2.5"
pydantic-settings = "^2.1"
aiohttp = "^3.9"
uvicorn = "^0.24"
pyyaml = "^6.0"

[tool.poetry.scripts]
telenotif = "telenotif.cli.commands:main"
```

**Installation**:
```bash
pip install telenotif
```

### Docker Support

**Single Dockerfile** (in package):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install telenotif
CMD ["telenotif", "run"]
```

**User mounts config**:
```bash
docker run -v ./config.yaml:/app/config.yaml -p 8000:8000 telenotif
```

### Free Hosting Platforms

**Render.com**:
- Create web service from GitHub repo
- Add environment variables (bot token, API key)
- Auto-deploy on push

**Railway.app**:
- Connect GitHub repo
- Set environment variables
- One-click deploy

**Fly.io**:
- `fly launch` from project directory
- `fly secrets set BOT_TOKEN=xxx`
- Deploy globally

---

## Phase 9: Testing

### Package Testing

**Unit tests** (pytest):
- Config loading and validation
- Plugin discovery
- Formatter output
- Bot message construction

**Integration tests**:
- End-to-end flow with mock Telegram API
- Plugin loading from filesystem
- API authentication

**No user testing needed** - package is pre-tested

### User Testing Support

**Test mode in config**:
```yaml
bot:
  token: "${BOT_TOKEN}"
  test_mode: true  # Logs messages instead of sending
```

**Mock responses** for development without bot token

---

## Phase 10: Documentation

### README (Quick Start)

```markdown
# TeleNotif - Telegram Notifications Made Simple

## Installation
pip install telenotif

## Quick Start
1. Create project: `telenotif init my_notifier`
2. Edit config.yaml (add bot token and endpoints)
3. Run: `telenotif run`
4. Send notification:
   curl -X POST http://localhost:8000/notify/orders \
     -H "Content-Type: application/json" \
     -d '{"message": "New order received"}'

## Configuration
See config.yaml for all options

## Custom Plugins
See plugins/example_formatter.py
```

### Full Documentation

**Sections**:
1. Installation & Setup (5 min read)
2. Configuration Reference (all YAML options)
3. Plugin Development (with examples)
4. API Reference (request/response formats)
5. Deployment Guide (Render, Railway, Docker)
6. Troubleshooting (common errors)

**No complex architecture docs** - keep it simple

---

## Implementation Roadmap

### Week 1: Core Framework
- [ ] Package structure
- [ ] Config loading (Pydantic models)
- [ ] Plugin interfaces
- [ ] Plugin discovery system

### Week 2: Telegram Integration
- [ ] Bot sender with aiohttp
- [ ] Retry logic
- [ ] Support all message types (text, images)
- [ ] Handle all chat types

### Week 3: FastAPI Server
- [ ] Dynamic route registration
- [ ] Request validation
- [ ] API key authentication
- [ ] Error handling

### Week 4: CLI & DX
- [ ] `telenotif init` command
- [ ] `telenotif run` command
- [ ] Project scaffolding
- [ ] Built-in formatters (plain, markdown)

### Week 5: Testing & Docs
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] README and quickstart
- [ ] Full documentation

### Week 6: Release
- [ ] PyPI package setup
- [ ] Docker image
- [ ] Deployment guides
- [ ] Example projects
- [ ] v1.0.0 release

---

## Success Criteria

**Must Have**:
- ✓ Install with `pip install telenotif`
- ✓ Configure with single YAML file
- ✓ Support all Telegram chat types
- ✓ Send text and images
- ✓ Custom endpoints via config
- ✓ Plugin system for formatters
- ✓ Works on free hosting (Render/Railway)

**Should Have**:
- ✓ API key authentication
- ✓ Retry logic for failures
- ✓ Health check endpoint
- ✓ CLI for project setup
- ✓ Clear error messages

**Nice to Have** (post-v1.0):
- Rate limiting per endpoint
- Message queuing (if needed)
- Webhook signature verification
- Multiple bot support in one instance

---

## Key Design Decisions

### What Makes It Simple

1. **No database**: Stateless - just forward requests
2. **No job queue**: Synchronous send (async handled by FastAPI)
3. **No templates**: Just format dicts to strings
4. **Single config file**: Everything in one place
5. **Minimal dependencies**: FastAPI, Pydantic, aiohttp only

### What Makes It Solid

1. **Type safety**: Pydantic everywhere
2. **Error handling**: Retry logic + clear errors
3. **Testable**: Mock-friendly architecture
4. **Extensible**: Plugin system without complexity
5. **Production-ready**: Logging, health checks, auth

### What We're NOT Building

- ❌ Dashboard/UI (use Telegram itself)
- ❌ Database for history (use logs)
- ❌ Complex queuing (use external service if needed)
- ❌ Multi-channel (Slack, Discord) - Telegram only
- ❌ Template engines (Jinja2) - just formatters
- ❌ User management - just API keys

---

## Example Usage Flow

### 1. Install & Setup
```bash
pip install telenotif
telenotif init my_notifier
cd my_notifier
# Edit config.yaml with bot token
```

### 2. Configure Endpoints
```yaml
endpoints:
  - path: "/notify/orders"
    chat_id: "-1001234567890"
    formatter: "plain"
```

### 3. Run Server
```bash
telenotif run
# Server running on http://localhost:8000
```

### 4. Send Notification
```bash
curl -X POST http://localhost:8000/notify/orders \
  -H "Content-Type: application/json" \
  -d '{"message": "New order from John", "order_id": 123}'
```

### 5. Receive in Telegram
```
[Your Bot in Channel]
message: New order from John
order_id: 123
```

**That's it. Simple.**

---

## Notes

**Why this approach**:
- Solves 80% of use cases with 20% complexity
- Deployable in 10 minutes (install → config → run)
- Maintainable by junior devs
- No unnecessary abstractions

**When to extend**:
- If you need custom formatting → add plugin
- If you need authentication → enable API key
- If you need monitoring → enable metrics endpoint
- If you need more features → fork and modify

The goal is **simple, not minimal**. It does what you need, nothing more.
