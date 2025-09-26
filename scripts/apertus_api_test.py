import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("APERTUS_API_KEY"),
    base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"
)

stream = client.chat.completions.create(
    model="swiss-ai/Apertus-70B",
    messages=[
        {"role": "system", "content": "You are a travel agent. Be descriptive and helpful"},
        {"role": "user", "content": "What are the best places to visit in Switzerland?"}
    ],
    stream=True
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
