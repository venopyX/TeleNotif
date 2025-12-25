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
curl -X POST http://localhost:8000/notify/orders \
  -H "Content-Type: application/json" \
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
