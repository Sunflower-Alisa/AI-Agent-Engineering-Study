import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
_VENV = os.path.join(
    os.path.dirname(__file__), "../day01-agent-loop/.venv/Lib/site-packages"
)
sys.path.insert(0, _VENV)
os.environ["PATH"] = (
    os.path.join(os.path.dirname(__file__), "../day01-agent-loop/.venv/Scripts")
    + ";"
    + os.environ.get("PATH", "")
)

from openai import OpenAI
from config import api_key, MODEL, cfg

client = OpenAI(base_url=cfg["base_url"], api_key=api_key)

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