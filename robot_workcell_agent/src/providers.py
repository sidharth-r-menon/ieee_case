"""Azure OpenAI provider configuration for Robot Workcell Design Agent.

Compatible with pydantic-ai >=1.55 (Provider-based API).
"""

import logging
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncAzureOpenAI
from src.settings import load_settings

logger = logging.getLogger(__name__)


def get_llm_model() -> Model:
    """
    Build Azure OpenAI model for the agent.
    
    Returns:
        OpenAIModel configured for Azure with credentials from .env
        
    Raises:
        ValueError: If Azure credentials are missing
    """
    settings = load_settings()
    
    if not settings.azure_api_key:
        raise ValueError(
            "AZURE_OPENAI_API_KEY is required. "
            "Set it in .env file or environment variables."
        )
    
    if not settings.azure_endpoint:
        raise ValueError(
            "AZURE_OPENAI_ENDPOINT is required. "
            "Set it in .env file (e.g., https://your-resource.openai.azure.com/)"
        )

    azure_client = AsyncAzureOpenAI(
        api_key=settings.azure_api_key,
        api_version=settings.azure_api_version,
        azure_endpoint=settings.azure_endpoint,
    )
    
    prov = OpenAIProvider(openai_client=azure_client)
    model = OpenAIModel(settings.azure_deployment_name, provider=prov)
    
    logger.info(
        f"azure_openai_initialized: deployment={settings.azure_deployment_name}, "
        f"endpoint={settings.azure_endpoint}"
    )
    
    return model
