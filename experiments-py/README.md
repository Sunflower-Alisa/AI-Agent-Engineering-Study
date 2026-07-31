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
experiments-py/
├── README.md          ← 本文件
├── config.py          ← 全局 LLM 配置（API 密钥、模型、地址）
├── .venv/             ← 统一虚拟环境（chromadb + openai）
│
└── week01/            ← 第一周：Agent 基础
    ├── day01-agent-loop/    ← Agent Loop 基础实现
    │   ├── agent.py
    │   └── tools.py
    ├── day02-tool-calling/  ← Tool Calling 实现
    │   ├── agent.py
    │   ├── tools.py
    │   └── main.py
    ├── day03-memory/        ← Memory 记忆模块
    └── day04-planning/      ← Planning 计划与重规划
```

## 运行

所有实验共用 `experiments-py/.venv` 统一虚拟环境（已安装 chromadb + openai）。
通过 site-packages 中的 `experiments.pth` 自动将 `experiments-py/` 加入 sys.path，因此各 .py 无需再做环境引入。

```bash
# 设置 API 密钥
set DEEPSEEK_API_KEY=sk-xxx

# 用统一 venv 运行对应实验
cd week01/day02-tool-calling
..\..\.venv\Scripts\python.exe main.py

# 或激活 venv 后直接运行
..\..\.venv\Scripts\activate
python main.py
```
