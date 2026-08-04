from openai import OpenAI
from config import api_key, MODEL, cfg

client = OpenAI(base_url=cfg["base_url"], api_key=api_key)


def chat(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
