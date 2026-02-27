
import os
import re
from openai import AsyncAzureOpenAI, AsyncOpenAI
from dotenv import load_dotenv
from src.settings import load_settings

# Load environment variables from .env file
load_dotenv()

def get_llm_client():
    settings = load_settings()
    provider = settings.model_provider.lower()
    if provider == "azure":
        # Return the native async AzureOpenAI client
        return AsyncAzureOpenAI(
            api_key=settings.azure_api_key,
            api_version=settings.azure_api_version,
            azure_endpoint=settings.azure_endpoint
        )
    elif provider == "qwen":
        # Use the proper AsyncOpenAI client — pydantic-ai's OpenAIProvider requires a
        # fully-compliant async client (not a hand-rolled wrapper) for tool-calling to work.
        # vLLM serves an OpenAI-compatible API so AsyncOpenAI works directly.
        return AsyncOpenAI(
            base_url=settings.qwen_api_base_url,
            api_key=settings.qwen_api_key,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


def clean_llm_response(text: str) -> str:
    """
    Cleans the LLM response. Removes <think>...</think> tags for Qwen/local provider.
    """
    settings = load_settings()
    provider = settings.model_provider.lower()
    if provider == "qwen":
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()
