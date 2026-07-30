# Day02 — Tool Calling（工具调用）

## 知识点

使用 OpenAI 兼容的 **Function Calling API**，LLM 原生支持 `tools` 参数，返回结构化的 `tool_calls` 而非靠 JSON Prompt 约定。这是生产级 Agent 的标准做法。

## 文件说明

| 文件 | 职责 |
|---|---|
| `Agent.cs` | Observe → Think(`ChatWithToolsAsync`) → Act(解析 tool_calls → 分发) → Run |
| `Tools.cs` | 工具定义（`ToolDefinition` 列表 + 函数映射 `Dictionary`） |
| `Program.cs` | 交互式入口 |

## 运行

```bash
dotnet run --project Day02.ToolCalling
```

## 执行流程

```
用户输入  →  消息列表 + tools 定义  →  LLM (Function Calling API)
                                       ↓
                             返回 tool_calls
                                    ↓
                   解析 → 按 name 查字典 → 执行函数
                                    ↓
                      tool 结果 + tool_call_id 追加到消息
                                    ↓
                              LLM 生成最终回答
```

## 工具说明

| 工具 | 参数 | 说明 |
|---|---|---|
| `calculate` | `expression: string` | 数学表达式计算，如 `"2+3*4"` |
| `get_time` | `city: string` | 查询指定城市当前时间（支持北京/纽约/伦敦等） |

## 关键实现细节

- `ToolDefinition.Parameters` 使用匿名类型定义 JSON Schema，通过 `System.Text.Json` 自动序列化
- `Agent.cs` 中 `assistant` 消息同时保存 `content` 和 `tool_calls`，`tool` 消息携带 `tool_call_id`，确保满足 API 协议
- 使用 `DataTable.Compute` 实现表达式求值，无需引入第三方计算库
