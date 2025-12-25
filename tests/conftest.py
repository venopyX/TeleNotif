"""Pytest configuration and fixtures"""

import tempfile

import pytest
import yaml


@pytest.fixture
def sample_config():
    """Sample configuration dictionary"""
    return {
        "bot": {
            "token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "test_mode": True,
        },
        "templates": {
            "test_template": "Hello {name}!",
        },
        "endpoints": [
            {
                "path": "/notify/test",
                "chat_id": "123456789",
                "formatter": "plain",
            }
        ],
        "server": {"host": "0.0.0.0", "port": 8000},
        "logging": {"level": "INFO"},
    }


@pytest.fixture
def config_file(sample_config):
    """Create temporary config file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sample_config, f)
        return f.name


@pytest.fixture
def mock_bot():
    """Mock Telegram bot for testing"""
    from telenotif.core.bot import TelegramBot

    return TelegramBot(token="test_token", test_mode=True)
