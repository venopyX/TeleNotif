# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2025-12-26

### Added
- Initial release
- FastAPI server with dynamic endpoint registration
- Plugin system with IFormatter and IPlugin interfaces
- Built-in formatters: plain text and Markdown
- Jinja2 template engine with conditionals, loops, and filters
- Custom labels for field display names
- Field mapping with dot notation for nested JSON
- Single image and photo gallery support (up to 10 images)
- Multiple chat_ids for broadcast messaging
- Inline keyboard buttons with dynamic Jinja2 templates
- Webhook support for receiving Telegram updates
- Command handlers (/start, /help, etc.)
- Callback handlers for button clicks
- API key authentication
- Automatic retry with exponential backoff
- MarkdownV2 auto-escaping
- CLI commands: init, run, validate, webhook (setup/info/delete)
- Health check endpoint
- Structured JSON error responses
- Chat ID validation with helpful warnings
- Test mode for development

### Documentation
- Comprehensive README with quick start guide
- Detailed USAGE.md with examples
- FUTURE.md roadmap
- TODO.md tracking

## [Unreleased]

### Planned
- Document/file support
- Video support
- Location sharing
- Prometheus metrics
- Rate limiting
