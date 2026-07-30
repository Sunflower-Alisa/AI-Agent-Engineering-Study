# Experiments

本目录包含 AI Agent 工程化的系列实验代码。

## config.py 说明

`config.py` 是全局配置文件，统一管理 LLM 提供商配置。它通过环境变量动态选择：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `LLM_PROVIDER` | 选择 LLM 提供商：`deepseek` 或 `openai` | `deepseek` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |

使用方法：各实验中的 `agent.py` 通过 `from config import api_key, MODEL, cfg` 引入配置，无需在每个文件中重复写 API 地址和密钥。

## 目录结构

```
experiments/
├── README.md          ← 本文件
├── config.py          ← 全局 LLM 配置（API 密钥、模型、地址）
│
└── week01/            ← 第一周：Agent 基础
    ├── day01-agent-loop/    ← Agent Loop 基础实现
    │   ├── agent.py
    │   └── tools.py
    └── day02-tool-calling/  ← Tool Calling 实现
        ├── agent.py
        ├── tools.py
        └── main.py
```

## 运行

```bash
# 进入对应实验目录
cd week01/day02-tool-calling

# 确保虚拟环境已安装依赖
python -m venv .venv
.venv\Scripts\activate
pip install openai python-dotenv

# 设置 API 密钥
set DEEPSEEK_API_KEY=sk-xxx

# 运行
python main.py
```
