from openai import OpenAI
from config import cfg,api_key,MODEL
import json
import re

client = OpenAI(base_url=cfg["base_url"],api_key=api_key)

def chat(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content

def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)
