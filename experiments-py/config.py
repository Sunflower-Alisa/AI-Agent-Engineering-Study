import os

provider = os.getenv("LLM_PROVIDER", "deepseek")

config = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "model": "deepseek-v4-flash",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4o-mini",
    },
}

if provider not in config:
    raise ValueError(f"未知 LLM 提供商: {provider}，可选: deepseek, openai")

cfg = config[provider]
api_key = cfg["api_key"]
if not api_key:
    raise ValueError(f"请设置 {'DEEPSEEK_API_KEY' if provider == 'deepseek' else 'OPENAI_API_KEY'} 环境变量")

MODEL = cfg["model"]