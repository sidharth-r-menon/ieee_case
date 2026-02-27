"""
Shared LLM provider configuration for all comparison pipelines.

Reuses the same Azure OpenAI credentials from the parent project's .env file.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Load .env from robot_workcell_agent directory
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_ENV_PATH)
except ImportError:
    logger.warning("python-dotenv not installed – reading env vars from OS only")


@dataclass
class ComparisonConfig:
    """Configuration shared across all comparison pipelines."""

    # Azure OpenAI
    azure_api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    azure_endpoint: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    azure_api_version: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"))
    azure_deployment: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"))

    # Evaluation settings
    max_iterations: int = 10  # Default; override for full eval
    timeout_per_stage_s: int = 120
    enable_genesis: bool = False  # Stage 3 genesis execution (requires GPU)

    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    skills_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "skills")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "logs")
    workcell_components_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent / "workcell_components"
    )
    mujoco_menagerie_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent / "mujoco_menagerie"
    )

    def __post_init__(self):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        if not self.azure_api_key:
            logger.warning("AZURE_OPENAI_API_KEY not set – LLM calls will fail")

    def get_openai_client(self):
        """Get a synchronous Azure OpenAI client."""
        from openai import AzureOpenAI
        return AzureOpenAI(
            api_key=self.azure_api_key,
            api_version=self.azure_api_version,
            azure_endpoint=self.azure_endpoint,
        )

    def get_async_openai_client(self):
        """Get an async Azure OpenAI client."""
        from openai import AsyncAzureOpenAI
        return AsyncAzureOpenAI(
            api_key=self.azure_api_key,
            api_version=self.azure_api_version,
            azure_endpoint=self.azure_endpoint,
        )


def get_config() -> ComparisonConfig:
    """Get the shared comparison configuration."""
    return ComparisonConfig()
