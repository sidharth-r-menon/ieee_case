"""Settings configuration for Robot Workcell Design Agent."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load .env from robot_workcell_agent directory
load_dotenv(Path(__file__).parent.parent / ".env")


@dataclass
class Settings:
    """Application settings loaded from environment variables with fallbacks."""

    # Skills Configuration - local path
    skills_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "skills")

    # Azure OpenAI Configuration (Required)
    azure_api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    azure_endpoint: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    azure_api_version: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"))
    azure_deployment_name: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"))

    # Logfire Integration (Disabled by default)
    logfire_token: Optional[str] = field(default_factory=lambda: os.getenv("LOGFIRE_TOKEN", None))
    logfire_service_name: str = "robot-workcell-agent"
    logfire_environment: str = "development"


# Singleton settings instance
_settings: Optional[Settings] = None


def load_settings() -> Settings:
    """Load settings (cached singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
