from openai import OpenAI
from langchain_openai import ChatOpenAI
import os
from langchain_google_genai import ChatGoogleGenerativeAI

APERTUS_MODEL_NAME = "swiss-ai/Apertus-70B"
APERTUS_BASE_URL = "https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"


class OpenaiApertus(OpenAI):
    """OpenAI based integration"""
    model = APERTUS_MODEL_NAME

    def __init__(self, api_key: str, **kwargs):
        super().__init__(
            api_key=api_key,
            base_url=APERTUS_BASE_URL,
            **kwargs,
        )


GEMINI_LLM = os.getenv("GEMINI_LLM", "FALSE") == "TRUE"
if GEMINI_LLM:
    print("STARTING WITH GEMINI")
    class LangchainApertus(ChatGoogleGenerativeAI):
        def __init__(self, api_key: str, **kwargs):
            super().__init__(
                model="gemini-2.5-flash-lite",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # other params...
            )
else:
    print("STARTING WITH APERTUS")
    class LangchainApertus(ChatOpenAI):
        """Langchain based integration"""
        def __init__(self, api_key: str, **kwargs):
            
            super().__init__(
                openai_api_key=api_key,
                model=APERTUS_MODEL_NAME,
                base_url=APERTUS_BASE_URL,
                **kwargs,
            )




if __name__ == "__main__":
    import os
    llm = LangchainApertus(api_key=os.environ.get("API_KEY"))
    print(llm.invoke("Hello world!"))