# Day03 — Memory（记忆模块）

## 知识点

Agent 的**记忆机制**：将对话历史或知识存储下来，在后续交互中检索并注入上下文。提供两种集成模式：

1. **代码控制型**（`AgentWithMemory`）— 开发者硬编码：每次对话前自动 search，对话后自动 save
2. **Tool 决策型**（`MemoryToolAgent`）— 将记忆 CRUD 封装为 Tool，由 LLM 自主决定何时操作记忆

## 文件说明

| 文件 | 职责 |
|---|---|
| `MemoryStore.cs` | 记忆存储引擎：`ConcurrentDictionary` + JSON 文件持久化，Jaccard 相似度搜索 |
| `AgentWithMemory.cs` | 代码控制型 Agent：自动检索+自动保存 |
| `MemoryToolAgent.cs` | Tool 决策型 Agent：save/search/delete/count 四个记忆 Tool |
| `Program.cs` | 入口，支持 1/2 切换两种模式 |

## 运行

```bash
dotnet run --project Day03.Memory
# 然后选择模式 1 或 2
```

## MemoryStore API

| 方法 | 说明 |
|---|---|
| `Save(id, text, metadata)` | 保存一条记忆 |
| `Retrieve(id)` | 根据 ID 获取 |
| `Search(query, k)` | 关键词搜索，Jaccard 相似度排序 |
| `Update(id, text, metadata)` | 更新已有记忆 |
| `Delete(id)` | 删除指定记忆 |
| `Count()` | 记忆总数 |

数据自动持久化到 `bin/Debug/net10.0/memory.json`。

## 两种模式对比

| 维度 | 代码控制型 | Tool 决策型 |
|---|---|---|
| 谁决定搜/存 | 开发者 | LLM |
| 实现复杂度 | 低 | 高（需定义 Tool + 解析 tool_calls） |
| 灵活性 | 固定策略 | LLM 可自主判断何时需要记忆 |
| 适用场景 | 简单场景、学习演示 | 复杂任务、生产场景 |
