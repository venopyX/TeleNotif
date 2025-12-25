# TeleNotif

> Simple, powerful Telegram notification framework with plugin support

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

TeleNotif receives HTTP webhooks and forwards them as formatted Telegram messages. Perfect for alerts, order notifications, monitoring, CI/CD pipelines, and any system that needs to notify users via Telegram.

## Features

- 🚀 **Simple** - Install, configure, run in under 5 minutes
- 🔌 **Plugin System** - Custom formatters without touching core code
- 📱 **All Chat Types** - Private chats, groups, supergroups, channels
- 🖼️ **Rich Media** - Single images, photo galleries (up to 10)
- 🏷️ **Custom Labels** - Map `order_id` → `🆔 Order ID`
- 🔀 **Field Mapping** - Map nested JSON fields with dot notation
- 🎨 **Formatters** - Plain text, Markdown, or custom plugins
- 🔒 **Secure** - API key authentication
- ♻️ **Reliable** - Automatic retries with exponential backoff
- 🐳 **Docker Ready** - Easy containerized deployment

## Quick Start

### 1. Install

```bash
pip install telenotif
```

### 2. Create Project

```bash
telenotif init my_notifier
cd my_notifier
```

### 3. Configure

Edit `config.yaml`:

```yaml
bot:
  token: "${TELEGRAM_BOT_TOKEN}"

endpoints:
  - path: "/notify/orders"
    chat_id: "-1001234567890"
    formatter: "plain"
```

### 4. Run

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
telenotif run
```

### 5. Send Notification

```bash
curl -X POST http://localhost:8000/notify/orders \
  -H "Content-Type: application/json" \
  -d '{"message": "New order received!", "order_id": 123}'
```

## Documentation

- [USAGE.md](USAGE.md) - Complete usage guide with examples
- [FUTURE.md](FUTURE.md) - Roadmap and planned features

## Configuration Reference

### Bot Configuration

```yaml
bot:
  token: "${TELEGRAM_BOT_TOKEN}"  # Bot token (supports env vars)
  test_mode: false                 # Log instead of sending (for testing)
```

### Templates

```yaml
templates:
  order_received: |
    🛒 *New Order \#{{ order_id }}*
    
    Customer: {{ customer }}
    Total: {{ total }}
```

### Endpoint Configuration

```yaml
endpoints:
  - path: "/webhook/orders"        # HTTP endpoint path
    chat_id: "8345389653"          # Telegram chat/group/channel ID
    formatter: "markdown"          # plain, markdown, or plugin name
    template: "order_received"     # Use template instead of formatter
    parse_mode: "MarkdownV2"       # Telegram parse mode
    labels:                        # Custom display labels
      order_id: "🆔 Order"
      customer: "👤 Customer"
    field_map:                     # Map incoming fields
      image_url: "product.photo"   # Supports dot notation
      image_urls: "product.gallery"
```

### Server Configuration

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  api_key: "${API_KEY}"            # Optional authentication

logging:
  level: "INFO"                    # DEBUG, INFO, WARNING, ERROR
```

## CLI Commands

```bash
telenotif init <name>     # Create new project
telenotif run             # Start server
telenotif run --reload    # Start with auto-reload (dev)
telenotif validate        # Validate config file
telenotif --version       # Show version
```

## Custom Plugins

Create `plugins/my_formatter.py`:

```python
from telenotif import IPlugin

class MyFormatter(IPlugin):
    @property
    def name(self):
        return "my_formatter"
    
    def format(self, payload: dict, config: dict) -> str:
        prefix = config.get("prefix", "📢")
        return f"{prefix} {payload.get('message', '')}"
```

Use in config:

```yaml
endpoints:
  - path: "/notify"
    chat_id: "123456789"
    formatter: "my_formatter"
    plugin_config:
      prefix: "🔔 Alert:"
```

## API Response

Success:
```json
{
  "status": "sent",
  "message_id": 123,
  "chat_id": "8345389653"
}
```

Error (structured JSON):
```json
{
  "detail": {
    "error": "invalid_api_key",
    "message": "Invalid or missing API key"
  }
}
```

Error codes: `invalid_api_key`, `formatter_not_found`, `send_failed`

## Getting Your Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Or send a message to your bot and check:
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getUpdates
   ```

## License

MIT License - see [LICENSE](LICENSE) for details.
