"""Apertus model provider for the backend agent."""

import os
from typing import Optional
from apertus.apertus import LangchainApertus
from core.config import settings


def get_apertus_model(api_key: Optional[str] = None, **kwargs) -> LangchainApertus:
    """
    Get the Apertus LLM model for use in the agent.

    Args:
        api_key: API key for Apertus. If None, will try to get from environment.
        **kwargs: Additional kwargs passed to LangchainApertus constructor.

    Returns:
        Configured LangchainApertus instance.

    Raises:
        ValueError: If no API key is provided or found in environment.
    """
    if api_key is None:
        api_key = settings.APERTUS_API_KEY or os.getenv("API_KEY")

    if not api_key:
        raise ValueError(
            "API key for Apertus is required. "
            "Provide it as argument or set the `APERTUS_API_KEY` environment variable."
        )

    return LangchainApertus(api_key=api_key, **kwargs)
