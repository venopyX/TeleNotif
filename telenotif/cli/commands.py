"""Command-line interface for TeleNotif"""

from pathlib import Path

import click
import uvicorn
import yaml


@click.group()
@click.version_option(version="0.9.0")
def cli():
    """TeleNotif - Simple Telegram Notification Framework"""
    pass


@cli.command()
@click.argument("project_name")
def init(project_name: str):
    """Initialize a new TeleNotif project"""
    project_path = Path(project_name)

    if project_path.exists():
        click.echo(f"Error: Directory '{project_name}' already exists", err=True)
        return

    click.echo(f"Creating project: {project_name}")

    project_path.mkdir()
    (project_path / "plugins").mkdir()

    config_content = """# TeleNotif Configuration

bot:
  token: "${TELEGRAM_BOT_TOKEN}"
  test_mode: false

endpoints:
  - path: "/notify/orders"
    chat_id: "-1001234567890"
    formatter: "plain"

  - path: "/notify/alerts"
    chat_id: "123456789"
    formatter: "markdown"
    parse_mode: "Markdown"

server:
  host: "0.0.0.0"
  port: 8000
  api_key: "${API_KEY}"

logging:
  level: "INFO"
"""
    (project_path / "config.yaml").write_text(config_content)

    main_content = '''"""TeleNotif server entry point"""

from telenotif import create_app

if __name__ == "__main__":
    import uvicorn

    app = create_app("config.yaml")
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    (project_path / "main.py").write_text(main_content)

    plugin_content = '''"""Example custom formatter plugin"""

from typing import Any
from telenotif import IPlugin


class OrderFormatter(IPlugin):
    """Custom formatter for order notifications"""

    @property
    def name(self) -> str:
        return "order_formatter"

    def format(self, payload: dict[str, Any], config: dict[str, Any]) -> str:
        prefix = config.get("prefix", "🛒 New Order")
        lines = [prefix, ""]

        if "order_id" in payload:
            lines.append(f"Order ID: #{payload['order_id']}")
        if "user" in payload:
            lines.append(f"Customer: {payload['user']}")
        if "total" in payload:
            lines.append(f"Total: ${payload['total']}")
        if "message" in payload:
            lines.append("")
            lines.append(payload["message"])

        return "\\n".join(lines)
'''
    (project_path / "plugins" / "example_formatter.py").write_text(plugin_content)

    (project_path / "requirements.txt").write_text("telenotif>=1.0.0\n")

    readme = f"""# {project_name}

TeleNotif notification service

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your-bot-token"
   export API_KEY="your-secret-key"
   ```

3. Edit `config.yaml` with your bot settings

4. Run the server:
   ```bash
   python main.py
   # or
   telenotif run
   ```
"""
    (project_path / "README.md").write_text(readme)

    (project_path / ".env.example").write_text(
        "TELEGRAM_BOT_TOKEN=your_bot_token_here\nAPI_KEY=your_api_key_here\n"
    )

    click.echo("✓ Project created successfully!")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  # Edit config.yaml with your settings")
    click.echo(f"  export TELEGRAM_BOT_TOKEN='your-token'")
    click.echo(f"  telenotif run")


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
@click.option("--host", default=None, help="Override host")
@click.option("--port", default=None, type=int, help="Override port")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def run(config: str, host: str, port: int, reload: bool):
    """Run the TeleNotif server"""
    if not Path(config).exists():
        click.echo(f"Error: Config file '{config}' not found", err=True)
        click.echo("Run 'telenotif init <project_name>' to create a new project")
        return

    with open(config) as f:
        config_data = yaml.safe_load(f)

    server_config = config_data.get("server", {})
    final_host = host or server_config.get("host", "0.0.0.0")
    final_port = port or server_config.get("port", 8000)

    click.echo(f"Starting TeleNotif server on {final_host}:{final_port}")

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
    """Validate configuration file"""
    if not Path(config).exists():
        click.echo(f"Error: Config file '{config}' not found", err=True)
        return

    try:
        from telenotif.core.config import AppConfig

        with open(config) as f:
            config_data = yaml.safe_load(f)

        app_config = AppConfig(**config_data)

        click.echo("✓ Configuration is valid!")
        click.echo(f"\nBot token: {'*' * 20}{app_config.bot.token[-4:]}")
        click.echo(f"Endpoints: {len(app_config.endpoints)}")

        for endpoint in app_config.endpoints:
            click.echo(f"  - {endpoint.path} → {endpoint.chat_id} ({endpoint.formatter})")

    except Exception as e:
        click.echo(f"✗ Configuration error: {e}", err=True)


if __name__ == "__main__":
    cli()
