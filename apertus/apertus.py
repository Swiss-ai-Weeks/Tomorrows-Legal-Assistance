from openai import OpenAI
from langchain_openai import ChatOpenAI


APERTUS_MODEL_NAME = "swiss-ai/Apertus-70B"
APERTUS_BASE_URL = https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1


class OpenaiApertus(OpenAI):
    """OpenAI based integration"""
    model = APERTUS_MODEL_NAME

    def __init__(self, api_key: str, **kwargs):
        super().__init__(
            api_key=api_key,
            base_url=APERTUS_BASE_URL,
            **kwargs,
        )


class LangchainApertus(ChatOpenAI):
    """Langchain based integration"""
    def __init__(self, api_key: str, **kwargs):
        super().__init__(
            openai_api_key=api_key,
            model=APERTUS_MODEL_NAME,
            base_url=APERTUS_BASE_URL,
            **kwargs,
        )
