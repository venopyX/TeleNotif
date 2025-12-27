# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-12-27

### Fixed
- **MarkdownV2 Formatting**: Reworked the MarkdownV2 escaping logic to correctly preserve formatting (e.g., bold, italic) while escaping special characters. This resolves issues where messages were sent without the intended formatting.
- **Jinja2 Templating**: Fixed a `TypeError` that occurred when using numerical comparisons in Jinja2 templates with `parse_mode: MarkdownV2`. The premature escaping of numbers as strings has been removed.

## [1.0.0] - 2025-12-27

### Added
- Universal environment variable support with `${VAR}` syntax for all config fields
- Support for default values with `${VAR:-default}` syntax
- CORS middleware with configurable origins
- Root endpoint (`GET /`) showing version, status, and API info
- Automatic .env file loading with python-dotenv
- Better error messages for missing environment variables

### Changed
- **BREAKING**: All config fields now support env vars (may affect existing configs)
- CLI init command now uses current development version in requirements.txt
- Improved init template with comprehensive environment variable examples

### Fixed
- Chat ID validation now works with environment variables
- CORS errors when accessing from frontend applications
- CLI init generating incorrect telegrify version requirements

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
