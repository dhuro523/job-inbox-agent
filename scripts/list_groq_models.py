"""
Lists models available to your Groq API key.
Run: uv run python -m scripts.list_groq_models
"""

from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

models = client.models.list()
for m in models.data:
    print(m.id)