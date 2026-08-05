from openai import OpenAI
from config import api_key, MODEL, cfg
import json
import re

client = OpenAI(base_url=cfg["base_url"], api_key=api_key)


def chat(prompt, max_retries=3):
    for attempt in range(max_retries):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
        content = response.choices[0].message.content
        if content and content.strip():
            return content
        if attempt < max_retries - 1:
            print(
                f"[llm] empty content, retry {attempt + 1}/{max_retries - 1} "
                f"(finish_reason={response.choices[0].finish_reason!r})"
            )
    raise RuntimeError("LLM returned empty content after retries")


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)
