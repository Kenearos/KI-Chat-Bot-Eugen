"""
Shared pytest fixtures for Eugen Bot tests
"""
import pytest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime, timedelta
import json


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables and logging handlers before each test"""
    import logging

    # Clean environment variables
    env_vars_to_clean = [
        'TWITCH_OAUTH_TOKEN', 'TWITCH_CHANNEL', 'TWITCH_BOT_NICKNAME',
        'PERPLEXITY_API_KEY', 'PERPLEXITY_MODEL', 'MAX_TOKENS',
        'DEBUG_MODE', 'AUTO_RECONNECT', 'RECONNECT_DELAY',
        'CONTEXT_RETENTION_HOURS', 'DATA_DIR', 'LOG_DIR'
    ]

    # Save original values
    original_env = {key: os.environ.get(key) for key in env_vars_to_clean}

    # Clear them
    for key in env_vars_to_clean:
        os.environ.pop(key, None)

    yield

    # Restore original values
    for key in env_vars_to_clean:
        os.environ.pop(key, None)
        if original_env[key] is not None:
            os.environ[key] = original_env[key]

    # Clean up logging handlers to prevent test interference
    for logger_name in ['eugen_main', 'eugen_api']:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.setLevel(logging.NOTSET)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_env_file(temp_dir):
    """Create a mock .env file for testing"""
    env_path = temp_dir / ".env"
    env_content = """TWITCH_OAUTH_TOKEN=oauth:test_token_12345
TWITCH_CHANNEL=#test_channel
TWITCH_BOT_NICKNAME=TestBot
PERPLEXITY_API_KEY=pplx-test-key-12345
PERPLEXITY_MODEL=sonar-pro
MAX_TOKENS=450
DEBUG_MODE=true
AUTO_RECONNECT=true
RECONNECT_DELAY=10
CONTEXT_RETENTION_HOURS=1
"""
    env_path.write_text(env_content)
    return env_path


@pytest.fixture
def mock_config_json(temp_dir):
    """Create a mock config.json file for testing"""
    config_path = temp_dir / "config.json"
    config_data = {
        "bot_name": "TestBot",
        "model": "sonar-pro",
        "max_tokens": 450,
        "debug_mode": True,
        "auto_reconnect": True,
        "reconnect_delay": 10,
        "context_retention_hours": 1
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return config_path


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history for testing"""
    now = datetime.now()
    return [
        {
            "role": "user",
            "content": "Hello bot!",
            "timestamp": (now - timedelta(minutes=10)).isoformat()
        },
        {
            "role": "assistant",
            "content": "Hi! How can I help?",
            "timestamp": (now - timedelta(minutes=9)).isoformat()
        },
        {
            "role": "user",
            "content": "What's the weather?",
            "timestamp": (now - timedelta(minutes=5)).isoformat()
        },
        {
            "role": "assistant",
            "content": "I don't have weather info.",
            "timestamp": (now - timedelta(minutes=4)).isoformat()
        }
    ]


@pytest.fixture
def old_conversation_history():
    """Old conversation history (beyond retention) for testing"""
    old_time = datetime.now() - timedelta(hours=2)
    return [
        {
            "role": "user",
            "content": "Old message",
            "timestamp": old_time.isoformat()
        },
        {
            "role": "assistant",
            "content": "Old response",
            "timestamp": (old_time + timedelta(minutes=1)).isoformat()
        }
    ]


@pytest.fixture
def mock_perplexity_response():
    """Mock successful Perplexity API response"""
    return {
        "id": "test-completion-123",
        "model": "sonar-pro",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the AI."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        }
    }


@pytest.fixture
def sample_messages():
    """Sample messages for API testing"""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
