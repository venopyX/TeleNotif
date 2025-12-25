# TeleNotif Usage Guide

Complete guide for using TeleNotif in your projects.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Sending Notifications](#sending-notifications)
- [Formatters](#formatters)
- [Custom Plugins](#custom-plugins)
- [Field Mapping](#field-mapping)
- [Authentication](#authentication)
- [Deployment](#deployment)

---

## Installation

### From PyPI

```bash
pip install telenotif
```

### From Source

```bash
git clone https://github.com/yourusername/telenotif.git
cd telenotif
pip install -e .
```

### Create a New Project

```bash
telenotif init my_notifier
cd my_notifier
```

This creates:
```
my_notifier/
├── config.yaml          # Main configuration
├── main.py              # Entry point
├── plugins/             # Custom plugins directory
│   └── example_formatter.py
├── requirements.txt
└── README.md
```

---

## Configuration

### Basic Configuration

```yaml
bot:
  token: "123456:ABC-DEF..."    # Your bot token from @BotFather

endpoints:
  - path: "/notify"
    chat_id: "8345389653"       # Your Telegram user/group/channel ID
    formatter: "plain"
```

### Environment Variables

Use `${VAR_NAME}` syntax for sensitive values:

```yaml
bot:
  token: "${TELEGRAM_BOT_TOKEN}"

server:
  api_key: "${API_KEY}"
```

Then set them:
```bash
export TELEGRAM_BOT_TOKEN="your-token"
export API_KEY="your-secret-key"
```

### Full Configuration Example

```yaml
bot:
  token: "${TELEGRAM_BOT_TOKEN}"
  test_mode: false              # Set true to log instead of send

endpoints:
  # Simple text notifications
  - path: "/notify/alerts"
    chat_id: "8345389653"
    formatter: "plain"

  # Formatted order notifications
  - path: "/webhook/orders"
    chat_id: "-1001234567890"   # Group/channel ID
    formatter: "markdown"
    parse_mode: "MarkdownV2"
    labels:
      order_id: "🆔 Order"
      customer: "👤 Customer"
      total: "💰 Total"
      status: "📦 Status"
    field_map:
      image_url: "product.thumbnail"
      image_urls: "product.images"

  # Custom plugin formatter
  - path: "/webhook/github"
    chat_id: "8345389653"
    formatter: "github_formatter"
    plugin_config:
      show_commits: true
      max_commits: 5

server:
  host: "0.0.0.0"
  port: 8000
  api_key: "${API_KEY}"

logging:
  level: "INFO"
```

---

## Sending Notifications

### Basic Text Message

```bash
curl -X POST http://localhost:8000/notify/alerts \
  -H "Content-Type: application/json" \
  -d '{"message": "Server is back online!"}'
```

### With Multiple Fields

```bash
curl -X POST http://localhost:8000/webhook/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 12345,
    "customer": "John Doe",
    "total": "$99.99",
    "status": "Processing"
  }'
```

Output with labels:
```
🆔 Order: 12345
👤 Customer: John Doe
💰 Total: $99.99
📦 Status: Processing
```

### With Single Image

```bash
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "New product added!",
    "image_url": "https://example.com/product.jpg"
  }'
```

### With Multiple Images (Gallery)

```bash
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Product gallery",
    "image_urls": [
      "https://example.com/photo1.jpg",
      "https://example.com/photo2.jpg",
      "https://example.com/photo3.jpg"
    ]
  }'
```

### With Authentication

```bash
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"message": "Authenticated notification"}'
```

### Override Chat ID Per Request

```bash
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Send to different chat",
    "chat_id": "987654321"
  }'
```

---

## Formatters

### Plain Formatter (Default)

Converts payload to simple `key: value` format.

```json
{"user": "John", "action": "login"}
```
→
```
user: John
action: login
```

### Markdown Formatter

Formats with Telegram Markdown. Keys named `title`, `heading`, or `header` become bold headers.

```json
{"title": "Alert!", "message": "CPU usage high", "value": "95%"}
```
→
```
*Alert!*
message: CPU usage high
value: 95%
```

**Note:** Use `parse_mode: "MarkdownV2"` in config for proper rendering.

---

## Custom Plugins

### Creating a Plugin

Create `plugins/my_formatter.py`:

```python
from typing import Any
from telenotif import IPlugin


class GitHubFormatter(IPlugin):
    """Format GitHub webhook payloads"""

    @property
    def name(self) -> str:
        return "github_formatter"

    def format(self, payload: dict[str, Any], config: dict[str, Any]) -> str:
        event = payload.get("action", "unknown")
        repo = payload.get("repository", {}).get("full_name", "unknown")
        sender = payload.get("sender", {}).get("login", "unknown")

        lines = [
            f"🔔 GitHub: {event}",
            f"📁 Repo: {repo}",
            f"👤 By: {sender}",
        ]

        # Use plugin config
        if config.get("show_commits") and "commits" in payload:
            max_commits = config.get("max_commits", 3)
            lines.append("\n📝 Commits:")
            for commit in payload["commits"][:max_commits]:
                msg = commit["message"].split("\n")[0][:50]
                lines.append(f"  • {msg}")

        return "\n".join(lines)
```

### Using the Plugin

```yaml
endpoints:
  - path: "/webhook/github"
    chat_id: "8345389653"
    formatter: "github_formatter"
    plugin_config:
      show_commits: true
      max_commits: 5
```

### Simple Formatter (IFormatter)

For plugins without config:

```python
from telenotif import IFormatter


class SimpleFormatter(IFormatter):
    def format(self, payload: dict) -> str:
        return f"Received: {payload}"
```

---

## Field Mapping

Map incoming payload fields to TeleNotif's expected fields using dot notation for nested objects.

### Configuration

```yaml
endpoints:
  - path: "/webhook/shopify"
    chat_id: "8345389653"
    formatter: "plain"
    field_map:
      image_url: "product.featured_image"
      image_urls: "product.images"
      chat_id: "meta.notify_target"
```

### Example Payload

```json
{
  "order_id": 123,
  "product": {
    "name": "T-Shirt",
    "featured_image": "https://example.com/main.jpg",
    "images": [
      "https://example.com/1.jpg",
      "https://example.com/2.jpg"
    ]
  },
  "meta": {
    "notify_target": "8345389653"
  }
}
```

TeleNotif automatically:
- Uses `product.featured_image` as the image
- Uses `product.images` for gallery
- Sends to `meta.notify_target` chat ID

---

## Authentication

### Enable API Key

```yaml
server:
  api_key: "${API_KEY}"
```

### Making Authenticated Requests

```bash
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"message": "Hello"}'
```

### Response Codes

- `200` - Success
- `401` - Invalid or missing API key
- `500` - Server error (check logs)

---

## Deployment

### Running Locally

```bash
# Development with auto-reload
telenotif run --reload

# Production
telenotif run --host 0.0.0.0 --port 8000
```

### Using Python Directly

```python
# main.py
from telenotif import create_app

if __name__ == "__main__":
    import uvicorn
    app = create_app("config.yaml")
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["telenotif", "run"]
```

```bash
docker build -t my-notifier .
docker run -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN="your-token" \
  -v $(pwd)/config.yaml:/app/config.yaml \
  my-notifier
```

### Docker Compose

```yaml
version: "3.8"
services:
  telenotif:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - API_KEY=${API_KEY}
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./plugins:/app/plugins
    restart: unless-stopped
```

### Systemd Service

```ini
# /etc/systemd/system/telenotif.service
[Unit]
Description=TeleNotif Notification Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/telenotif
Environment=TELEGRAM_BOT_TOKEN=your-token
ExecStart=/usr/local/bin/telenotif run
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable telenotif
sudo systemctl start telenotif
```

### Cloud Platforms

**Render.com:**
1. Connect GitHub repo
2. Set environment variables
3. Start command: `telenotif run --host 0.0.0.0 --port $PORT`

**Railway.app:**
1. Connect repo
2. Add environment variables
3. Deploy automatically

**Fly.io:**
```bash
fly launch
fly secrets set TELEGRAM_BOT_TOKEN=your-token
fly deploy
```

---

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "endpoints": 2,
  "formatters": ["plain", "markdown", "github_formatter"]
}
```

---

## Troubleshooting

### Bot not sending messages

1. Check bot token is correct
2. Ensure bot is added to the chat/group
3. For channels, bot must be admin
4. Check `telenotif validate` output

### Invalid chat_id

- User ID: positive number (`8345389653`)
- Group ID: negative number (`-123456789`)
- Supergroup/Channel: starts with `-100` (`-1001234567890`)
- Channel username: `@channel_name`

### Markdown parsing errors

Use `parse_mode: "MarkdownV2"` and ensure special characters are escaped. The markdown formatter handles this automatically.

### Rate limiting

TeleNotif automatically retries with exponential backoff when rate limited. For high-volume use, consider:
- Multiple bot tokens
- Message queuing
- Batching notifications

---

## Examples

### CI/CD Pipeline Notification

```bash
# In your CI script
curl -X POST https://your-server.com/notify/ci \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $NOTIFY_KEY" \
  -d "{
    \"title\": \"Build ${BUILD_STATUS}\",
    \"project\": \"${PROJECT_NAME}\",
    \"branch\": \"${BRANCH}\",
    \"commit\": \"${COMMIT_SHA:0:7}\",
    \"author\": \"${AUTHOR}\"
  }"
```

### E-commerce Order Notification

```yaml
# config.yaml
endpoints:
  - path: "/webhook/orders"
    chat_id: "-1001234567890"
    formatter: "markdown"
    parse_mode: "MarkdownV2"
    labels:
      id: "🆔 Order"
      customer_name: "👤 Customer"
      total_price: "💰 Total"
      items_count: "📦 Items"
    field_map:
      image_url: "line_items.0.image_url"
```

### Server Monitoring Alert

```python
import requests

def send_alert(metric, value, threshold):
    requests.post("http://localhost:8000/notify/alerts", json={
        "title": "⚠️ Alert",
        "metric": metric,
        "value": f"{value}%",
        "threshold": f"{threshold}%",
        "status": "CRITICAL" if value > threshold else "WARNING"
    })

# Usage
send_alert("CPU Usage", 95, 80)
```
