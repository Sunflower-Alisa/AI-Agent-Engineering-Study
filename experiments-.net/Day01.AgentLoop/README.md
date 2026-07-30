# Day01 — Agent 基础循环

## 知识点

AI Agent 最基础的 **Observe → Think → Act** 循环。LLM 被要求以 JSON 格式回复：若需要工具则返回 `{"action": "工具名"}`，否则返回 `{"answer": "直接回答"}`。

## 文件说明

| 文件 | 职责 |
|---|---|
| `Agent.cs` | 核心循环：System Prompt → 用户输入 → LLM 返回 JSON → 调用工具 or 回答 |
| `Program.cs` | 交互式入口，注册 `get_current_time` 和 `roll_dice` 两个工具 |

## 运行

```bash
dotnet run --project Day01.AgentLoop
```

## 执行流程

```
用户输入  →  System Prompt + 消息历史  →  LLM
                                          ↓
                                   JSON 解析
                                    ↙     ↘
                           有 action     有 answer
                              ↓              ↓
                         调用工具 → 结果    返回答案
                         追加到历史
```

## 工具说明

- `get_current_time` — 返回当前服务器时间
- `roll_dice` — 返回 1-6 随机数

## 注意

Agent 通过消息历史维护上下文，工具结果以 `user` 角色回写到对话中，让 LLM 知道这是工具执行的结果而非新用户提问。
