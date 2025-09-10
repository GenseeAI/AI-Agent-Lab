"""
Environment configuration utilities for the meta-agent system.
"""
import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
    _load_dotenv = load_dotenv
except ImportError:
    DOTENV_AVAILABLE = False
    _load_dotenv = None


def load_environment_variables():
    """Load environment variables from .env file if it exists."""
    if not DOTENV_AVAILABLE or _load_dotenv is None:
        return False

    # Look for .env file in the current directory
    env_path = Path(".env")
    if env_path.exists():
        _load_dotenv(env_path)
        return True

    # Look for .env file in the script's directory
    script_dir = Path(__file__).parent
    env_path = script_dir / ".env"
    if env_path.exists():
        _load_dotenv(env_path)
        return True

    return False


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for the specified LLM provider from environment variables."""

    # Try to load .env file first
    load_environment_variables()

    provider_upper = provider.upper()
    key_name = f"{provider_upper}_API_KEY"

    return os.getenv(key_name)


def get_default_llm_config() -> dict:
    """Get default LLM configuration from environment variables."""

    load_environment_variables()

    return {
        "provider": os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
        "model": os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
    }


def check_api_key_availability(provider: str) -> bool:
    """Check if API key is available for the specified provider."""

    api_key = get_api_key(provider)
    return api_key is not None and api_key.strip() != ""


def setup_environment():
    """Set up environment variables and return status information."""

    env_loaded = load_environment_variables()

    # Check available API keys
    openai_available = check_api_key_availability("openai")

    return {
        "env_file_loaded": env_loaded,
        "openai_key_available": openai_available,
        "dotenv_installed": DOTENV_AVAILABLE
    }
