# TeleNotif Future Roadmap

Ideas and planned features for future versions.

## Version 1.1 - Enhanced Messaging

### Inline Keyboards
Add interactive buttons to messages.

```yaml
endpoints:
  - path: "/notify/approval"
    chat_id: "8345389653"
    buttons:
      - text: "✅ Approve"
        callback: "approve"
      - text: "❌ Reject"
        callback: "reject"
```

### Message Templates
Pre-defined templates with variable substitution.

```yaml
templates:
  order_received: |
    🛒 *New Order #{order_id}*
    
    Customer: {customer}
    Total: {total}
    
    Items: {items_count}

endpoints:
  - path: "/orders"
    template: "order_received"
```

### Reply Markup
Support for reply keyboards and remove keyboard.

```yaml
endpoints:
  - path: "/survey"
    reply_keyboard:
      - ["👍 Good", "👎 Bad"]
      - ["📝 Feedback"]
```

---

## Version 1.2 - Advanced Media

### Document Support
Send files and documents.

```json
{
  "message": "Monthly report",
  "document_url": "https://example.com/report.pdf",
  "filename": "report_dec_2024.pdf"
}
```

### Video Support
Send videos with thumbnails.

```json
{
  "caption": "Product demo",
  "video_url": "https://example.com/demo.mp4",
  "thumbnail_url": "https://example.com/thumb.jpg"
}
```

### Audio/Voice Messages
```json
{
  "audio_url": "https://example.com/podcast.mp3",
  "title": "Episode 42",
  "performer": "TechTalk"
}
```

### Location Sharing
```json
{
  "message": "Order delivery location",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

---

## Version 1.3 - Reliability & Scale

### Message Queue Integration
Optional Redis/RabbitMQ queue for high-volume scenarios.

```yaml
queue:
  enabled: true
  backend: "redis"
  url: "redis://localhost:6379"
  retry_attempts: 5
  retry_delay: 60
```

### Batch Sending
Send to multiple chats in one request.

```json
{
  "message": "Broadcast announcement",
  "chat_ids": ["123", "456", "789"]
}
```

### Scheduled Messages
Schedule notifications for later delivery.

```json
{
  "message": "Reminder: Meeting in 1 hour",
  "schedule_at": "2024-12-26T10:00:00Z"
}
```

### Dead Letter Queue
Store failed messages for retry/inspection.

```yaml
dlq:
  enabled: true
  storage: "sqlite"  # or redis, postgres
  retention_days: 7
```

---

## Version 1.4 - Observability

### Prometheus Metrics
Built-in metrics endpoint.

```yaml
metrics:
  enabled: true
  path: "/metrics"
```

Metrics:
- `telenotif_messages_sent_total`
- `telenotif_messages_failed_total`
- `telenotif_request_duration_seconds`
- `telenotif_telegram_api_latency_seconds`

### Webhook Logging
Log all incoming webhooks for debugging.

```yaml
logging:
  level: "INFO"
  webhook_logging: true
  log_payloads: true  # Be careful with sensitive data
```

### Delivery Reports
Track message delivery status.

```yaml
tracking:
  enabled: true
  callback_url: "https://your-app.com/delivery-status"
```

---

## Version 1.5 - Multi-Channel

### Slack Integration
Send to Slack alongside Telegram.

```yaml
channels:
  telegram:
    token: "${TELEGRAM_BOT_TOKEN}"
  slack:
    webhook_url: "${SLACK_WEBHOOK_URL}"

endpoints:
  - path: "/notify/critical"
    targets:
      - type: telegram
        chat_id: "8345389653"
      - type: slack
        channel: "#alerts"
```

### Discord Integration
```yaml
channels:
  discord:
    webhook_url: "${DISCORD_WEBHOOK_URL}"
```

### Email Fallback
Send email if Telegram fails.

```yaml
channels:
  email:
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    username: "${EMAIL_USER}"
    password: "${EMAIL_PASS}"

endpoints:
  - path: "/notify/important"
    targets:
      - type: telegram
        chat_id: "8345389653"
    fallback:
      - type: email
        to: "admin@example.com"
```

---

## Version 1.6 - Security & Auth

### Webhook Signature Verification
Verify incoming webhooks from known sources.

```yaml
endpoints:
  - path: "/webhook/github"
    signature:
      header: "X-Hub-Signature-256"
      secret: "${GITHUB_WEBHOOK_SECRET}"
      algorithm: "sha256"
```

### Rate Limiting
Per-endpoint rate limits.

```yaml
endpoints:
  - path: "/notify"
    rate_limit:
      requests: 100
      period: 60  # seconds
```

### IP Allowlist
Restrict access by IP.

```yaml
security:
  ip_allowlist:
    - "192.168.1.0/24"
    - "10.0.0.0/8"
```

### JWT Authentication
Support JWT tokens alongside API keys.

```yaml
auth:
  jwt:
    secret: "${JWT_SECRET}"
    algorithm: "HS256"
```

---

## Version 1.7 - Developer Experience

### Web Dashboard
Simple web UI for:
- Viewing message history
- Testing endpoints
- Managing configuration
- Monitoring health

```yaml
dashboard:
  enabled: true
  path: "/admin"
  username: "admin"
  password: "${DASHBOARD_PASSWORD}"
```

### OpenAPI Schema
Auto-generated API documentation.

```yaml
docs:
  enabled: true
  path: "/docs"
```

### Config Hot Reload
Reload configuration without restart.

```bash
curl -X POST http://localhost:8000/admin/reload
```

### Plugin Marketplace
Community plugins repository.

```bash
telenotif plugin install github-formatter
telenotif plugin install shopify-orders
```

---

## Version 2.0 - Bot Framework

### Two-Way Communication
Handle incoming messages from users.

```yaml
bot:
  token: "${TELEGRAM_BOT_TOKEN}"
  handlers:
    - command: "/start"
      response: "Welcome to notifications!"
    - command: "/subscribe"
      action: "subscribe_user"
    - pattern: ".*help.*"
      response: "How can I help you?"
```

### User Subscriptions
Let users subscribe/unsubscribe from notifications.

```python
# Auto-generated endpoints
POST /subscribe    # User subscribes
DELETE /subscribe  # User unsubscribes
GET /subscribers   # List subscribers
```

### Conversation Flows
Multi-step interactions.

```yaml
flows:
  feedback:
    - ask: "How would you rate our service?"
      options: ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
      save_as: "rating"
    - ask: "Any comments?"
      save_as: "comment"
    - action: "save_feedback"
```

### Inline Queries
Respond to inline queries.

```yaml
inline:
  enabled: true
  handler: "search_products"
```

---

## Community Ideas

### Conditional Routing
Route messages based on payload content.

```yaml
endpoints:
  - path: "/notify"
    routes:
      - condition: "severity == 'critical'"
        chat_id: "-1001234567890"  # Alerts channel
      - condition: "severity == 'info'"
        chat_id: "8345389653"      # Personal chat
```

### Message Deduplication
Prevent duplicate messages within time window.

```yaml
deduplication:
  enabled: true
  window: 300  # seconds
  key_fields: ["order_id", "event_type"]
```

### Transformation Pipeline
Transform payload before formatting.

```yaml
endpoints:
  - path: "/webhook/raw"
    transform:
      - type: "jq"
        expression: "{order: .data.order_id, total: .data.amount}"
      - type: "enrich"
        lookup: "customers"
        key: "customer_id"
```

### A/B Testing
Test different message formats.

```yaml
endpoints:
  - path: "/notify"
    ab_test:
      - weight: 50
        formatter: "plain"
      - weight: 50
        formatter: "markdown"
```

---

## Contributing Ideas

Have an idea? We'd love to hear it!

1. Open an issue on GitHub
2. Describe the use case
3. Propose a configuration format
4. Discuss implementation approach

---

## Priority Matrix

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| Inline Keyboards | High | Medium | P1 |
| Message Templates | High | Low | P1 |
| Document Support | Medium | Low | P1 |
| Prometheus Metrics | High | Medium | P1 |
| Message Queue | High | High | P2 |
| Slack Integration | Medium | Medium | P2 |
| Web Dashboard | Medium | High | P2 |
| Webhook Signatures | High | Low | P2 |
| Rate Limiting | Medium | Low | P2 |
| Bot Framework | High | High | P3 |
| Conversation Flows | Medium | High | P3 |

---

## Version Timeline (Tentative)

- **v1.1** - Q1 2025: Enhanced Messaging
- **v1.2** - Q1 2025: Advanced Media
- **v1.3** - Q2 2025: Reliability & Scale
- **v1.4** - Q2 2025: Observability
- **v1.5** - Q3 2025: Multi-Channel
- **v1.6** - Q3 2025: Security & Auth
- **v1.7** - Q4 2025: Developer Experience
- **v2.0** - 2026: Bot Framework
