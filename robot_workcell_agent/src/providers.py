"""Azure OpenAI provider configuration for Robot Workcell Design Agent.

Compatible with pydantic-ai >=1.55 (Provider-based API).
"""

import logging
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.llm_client import get_llm_client
from src.settings import load_settings

logger = logging.getLogger(__name__)


def get_llm_model() -> Model:
    """
    Build LLM model for the agent, supporting Azure OpenAI and Qwen/local.
    Returns:
        OpenAIModel configured for the selected provider
    Raises:
        ValueError: If credentials are missing
    """
    settings = load_settings()
    llm_client = get_llm_client()
    provider = settings.model_provider.lower()
    if provider == "azure":
        deployment = settings.azure_deployment_name
        prov = OpenAIProvider(openai_client=llm_client)
        model = OpenAIModel(deployment, provider=prov)
    elif provider == "qwen":
        deployment = settings.qwen_base_model
        prov = OpenAIProvider(openai_client=llm_client)
        # WARNING: Hyperparameters must be passed at call time, not model construction
        model = OpenAIModel(deployment, provider=prov)
    else:
        raise ValueError(f"Unknown provider: {provider}")
    logger.info(f"llm_initialized: provider={provider}, deployment={deployment}")
    return model
