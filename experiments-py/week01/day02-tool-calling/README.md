# Day 02: Tool Calling Mini Agent

学习目标：理解 Agent 如何从"会思考"变成"能行动"，实现基础工具调用循环。

## Agent + Tool 工作逻辑

```
User
  ↓
LLM（接收用户问题，决定是否调用工具）
  ↓
Decision（选择工具 + 生成参数）
  ↓
Tool（执行工具，返回 Observation）
  ↓
LLM（结合 Observation 继续推理）
  ↓
Decision（完成 or 继续调用工具）
  ↓
...
  ↓
Answer（最终回答）
```

## 文件结构

```
day02-tool-calling/
├── main.py           ← 程序入口（交互式 CLI）
├── agent.py          ← Agent 核心循环（Observe → Think → Act → Run）
├── tools.py          ← 工具实现 + Schema 定义 + 函数映射字典
└── README.md
```

## Tools Schema（工具定义模版）

`tools.py` 中的 `tool_definitions` 是传给 LLM 的 API 工具描述，让 LLM 知道有哪些工具可用及如何调用。

```python
tool_definitions = [
    {
        "type": "function",                     # 固定值
        "function": {
            "name": "工具名称",                   # LLM 引用该工具时的标识
            "description": "工具功能描述",          # LLM 根据描述决定是否使用
            "parameters": {                      # 参数 Schema（JSON Schema 格式）
                "type": "object",
                "properties": {
                    "参数名": {
                        "type": "string",
                        "description": "参数说明"
                    }
                },
                "required": ["参数名"]             # 必填参数列表
            }
        }
    }
]
```

## 后端映射字典（Function Mapping）

`tool_definitions` 只描述接口，实际执行的 Python 函数通过 `tool_functions` 字典映射：

```python
tool_functions = {
    "get_time": get_time,      # 键 = 工具名，值 = 对应的 Python 函数
    "calculate": calculate,
}
```

当 LLM 返回 `tool_call.function.name = "get_time"` 时，`agent.py:act()` 通过 `self.functions[func_name]` 找到 `get_time` 函数并执行，返回结果再注入 LLM 上下文继续推理。

## 运行

```bash
cd experiments/week01/day02-tool-calling
.venv\Scripts\activate
python main.py
```

输入问题测试工具调用，输入 `exit` 或 `quit` 退出。

### 示例

```
User: 1+1+2
Agent: 1+1+2 = 4

User: 纽约现在几点
Agent: 纽约当前时间是 2026-07-29 08:30:00
```

