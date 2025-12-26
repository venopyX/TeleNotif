# Telegrify TODO

## ✅ Completed (v0.9.0)
- [x] Core package structure
- [x] FastAPI server with dynamic routes
- [x] Plugin system (IFormatter, IPlugin)
- [x] Plain & Markdown formatters
- [x] Jinja2 template engine
- [x] Custom labels for keys
- [x] Field mapping with dot notation
- [x] Single image & photo gallery support
- [x] API key authentication
- [x] Retry logic with exponential backoff
- [x] Health check endpoint
- [x] CLI (init, run, validate)
- [x] Structured JSON error responses
- [x] Chat ID validation warnings
- [x] MarkdownV2 auto-escaping
- [x] Documentation (README, USAGE, FUTURE)
- [x] Unit tests

---

## 🚀 Version 1.1 - Enhanced Messaging
- [ ] Inline keyboards (interactive buttons)
- [ ] Reply keyboards
- [ ] Remove keyboard support
- [ ] Button callback handling

## 🖼️ Version 1.2 - Advanced Media
- [ ] Document/file support (sendDocument)
- [ ] Video support (sendVideo)
- [ ] Audio/voice messages (sendAudio, sendVoice)
- [ ] Location sharing (sendLocation)
- [ ] Contact sharing (sendContact)
- [ ] Sticker support (sendSticker)

## ⚡ Version 1.3 - Reliability & Scale
- [ ] Message queue integration (Redis/RabbitMQ)
- [ ] Batch sending (multiple chat_ids)
- [ ] Scheduled messages (schedule_at)
- [ ] Dead letter queue for failed messages
- [ ] Circuit breaker pattern

## 📊 Version 1.4 - Observability
- [ ] Prometheus metrics endpoint
- [ ] Webhook payload logging
- [ ] Delivery reports/callbacks
- [ ] Request ID correlation (structlog)
- [ ] OpenTelemetry tracing

## 🌐 Version 1.5 - Multi-Channel
- [ ] Slack integration
- [ ] Discord integration
- [ ] Email fallback
- [ ] SMS fallback (Twilio)
- [ ] Microsoft Teams integration

## 🔒 Version 1.6 - Security & Auth
- [ ] Webhook signature verification (GitHub, Stripe, etc.)
- [ ] Rate limiting (per-endpoint)
- [ ] IP allowlist/blocklist
- [ ] JWT authentication
- [ ] OAuth2 support

## 🛠️ Version 1.7 - Developer Experience
- [ ] Web dashboard (message history, testing, config)
- [ ] OpenAPI/Swagger docs auto-generation
- [ ] Config hot reload
- [ ] Plugin marketplace / entry-point discovery
- [ ] CLI: `telegrify plugin install <name>`

## 🤖 Version 2.0 - Bot Framework
- [ ] Two-way communication (handle incoming messages)
- [ ] Command handlers (/start, /help, etc.)
- [ ] User subscriptions (subscribe/unsubscribe)
- [ ] Conversation flows (multi-step dialogs)
- [ ] Inline queries
- [ ] Callback query handling

---

## 💡 Community Ideas / Nice-to-Have
- [ ] Conditional routing (route by payload content)
- [ ] Message deduplication (prevent duplicates)
- [ ] Transformation pipeline (jq expressions)
- [ ] A/B testing for message formats
- [ ] Message editing (editMessageText)
- [ ] Message deletion (deleteMessage)
- [ ] Pin/unpin messages
- [ ] Chat actions (typing indicator)
- [ ] Polls (sendPoll)
- [ ] Silent messages (disable_notification)
- [ ] Message threading (reply_to_message_id)
- [ ] Forward messages
- [ ] Copy messages
- [ ] Webhook retry configuration (custom attempts/delays)
- [ ] Response caching
- [ ] Payload validation schemas (JSON Schema)
- [ ] Custom HTTP headers forwarding
- [ ] Proxy support for Telegram API
- [ ] Multiple bot tokens (load balancing)
- [ ] Timezone-aware scheduling
- [ ] Template inheritance (base templates)
- [ ] i18n / localization support
- [ ] Markdown to HTML converter
- [ ] Preview link control (disable_web_page_preview)

---

## 📋 Priority Matrix

| Priority | Features |
|----------|----------|
| **P1** | Inline keyboards, Document support, Prometheus metrics, Webhook signatures |
| **P2** | Message queue, Slack integration, Rate limiting, Web dashboard |
| **P3** | Bot framework, Conversation flows, Multi-channel |

---

## 🗓️ Timeline (Tentative)

| Version | Target | Focus |
|---------|--------|-------|
| v0.9.0 | ✅ Done | Core functionality |
| v1.0.0 | Q1 2025 | Stable release, bug fixes |
| v1.1.0 | Q1 2025 | Enhanced messaging |
| v1.2.0 | Q2 2025 | Advanced media |
| v1.3.0 | Q2 2025 | Reliability & scale |
| v1.4.0 | Q3 2025 | Observability |
| v1.5.0 | Q3 2025 | Multi-channel |
| v1.6.0 | Q4 2025 | Security |
| v1.7.0 | Q4 2025 | Developer experience |
| v2.0.0 | 2026 | Bot framework |
