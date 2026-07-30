# Day 03: Memory — Agent 的记忆系统

## Memory 在 Agent 中的作用

LLM 本身是无状态的——每次对话都是独立的，不记得之前说过什么。Memory 为 Agent 提供了**持久化记忆**能力，让 Agent 能够：

- **跨对话保持上下文**：记住用户偏好、历史问题、之前的结果
- **检索相关经验**：遇到类似问题时，参考过去的处理方式
- **积累知识**：从每次交互中学习，逐渐更了解用户

```
无 Memory 的 Agent:         有 Memory 的 Agent:

User: 我叫小明                User: 我叫小明
Agent: 你好                   Agent: 你好，小明！
                             (memory.save 记住了名字)
User: 我叫什么？              User: 我叫什么？
Agent: 我不知道               Agent: 你叫小明！
                             (memory.retrieve 查到了)
```

## 调用逻辑

```
                 用户输入
                     ↓
        ┌────────────────────────────┐
        │  ① RETRIEVE / SEARCH       │  ← 查历史记忆
        │  将相关记忆注入 Prompt      │
        └────────────────────────────┘
                     ↓
        ┌────────────────────────────┐
        │  ② LLM 推理（带记忆）       │
        └────────────────────────────┘
                     ↓
        ┌────────────────────────────┐
        │  ③ 执行 Tool（如果需要）    │
        └────────────────────────────┘
                     ↓
        ┌────────────────────────────┐
        │  ④ SAVE / UPDATE           │  ← 保存本次交互
        └────────────────────────────┘
                     ↓
                  返回答案
```

## 各操作的使用时机

### SAVE（保存）— 新信息产生时

| 时机 | 示例 |
|------|------|
| 用户主动提供个人信息 | “我叫小明”、“我在上海工作” |
| Agent 完成一次问答 | 保存 Q&A 对，后续可参考 |
| 工具返回了重要结果 | 查询到的数据、计算结果 |
| 用户表达了偏好 | “我喜欢简洁的回答”、“用中文回复” |

```python
memory.save("user_name", "小明", {"type": "profile"})
memory.save("qa:001", "Q: 1+1?\nA: 2", {"type": "qa"})
```

### RETRIEVE / SEARCH（检索）— 每次 LLM 调用前

| 时机 | 说明 |
|------|------|
| 用户发起新对话 | 先检索是否有相关历史 |
| LLM 需要上下文 | 将检索结果注入 system prompt |
| 解决用户问题前 | 查找类似问题的历史答案 |

```python
past = memory.search("小明", n_results=3)     # 语义搜索
profile = memory.retrieve("user_name")         # 精确 key 检索
```

### UPDATE（更新）— 信息发生变化时

| 时机 | 示例 |
|------|------|
| 用户的个人信息变更 | “我搬家到北京了”→ 更新城市 |
| 之前保存的信息有误 | 修正错误的记忆 |
| 状态发生变化 | 任务从“进行中”改为“已完成” |

```python
memory.update("user_city", "北京", {"type": "profile"})
```

### DELETE（删除）— 信息不再需要时

| 时机 | 示例 |
|------|------|
| 用户要求忘记 | “忘掉我的地址” |
| 隐私/合规要求 | 删除敏感信息 |
| 记忆过时/无效 | 清理过期缓存 |
| 达到存储上限 | 淘汰最不相关的记忆 |

```python
memory.delete("temp_cache_001")
```

## 记忆类型分类建议

```
短期记忆（Short-term）      长期记忆（Long-term）
──────────────────────────  ──────────────────────────
当前对话上下文              用户个人信息
临时工具结果                历史问答经验
一次性状态                  偏好设置
                            任务完成记录
→ 不需要持久化              → 需要 SAVE / RETRIEVE
→ 对话结束即丢弃             → 跨对话持久保存
```

## ChromaDB 说明

本项目的 Memory 使用 ChromaDB 作为向量数据库后端。

### 什么是 ChromaDB

ChromaDB 是一个开源向量数据库，专门用于存储和检索嵌入向量。相比 dict 存储，它能做**语义搜索**——找到"意思相近"的内容，而不仅仅是 key 精确匹配。

### 什么时候用 ChromaDB

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 仅需 key-value 精确存取 | dict / Redis | 简单、快 |
| 需要按语义搜索记忆 | ChromaDB | 支持模糊匹配和相似度排序 |
| 记忆量小（<100条） | dict 就够了 | 遍历搜索也能接受 |
| 记忆量大（>1000条） | ChromaDB 必要 | 语义索引保证检索效率 |
| Agent 需要跨对话回忆 | ChromaDB | 持久化到磁盘，重启不丢失 |

### 安装

```bash
pip install chromadb
```

### 基本用法

```python
from memory import Memory

m = Memory()                               # 数据持久化到 ./chroma_data/

# 存
m.save("user_name", "小明", {"type": "profile"})

# 精确检索（按 key）
val = m.retrieve("user_name")

# 语义搜索（按意思匹配）
results = m.search("喜欢什么", n_results=3)

# 更新
m.update("user_name", "小王", {"type": "profile"})

# 删除
m.delete("user_name")

# 统计
m.count()
```

### 存储后端

ChromaDB 使用 `PersistentClient`，数据默认保存在 `./chroma_data/` 目录，Agent 重启后记忆仍在。可通过 `Memory(path="自定义路径")` 指定位置。

## 在 Agent 中的集成示例

### 方式一：代码控制（agent_with_memory.py）

代码中显式调用 Memory 操作：

```python
def run(self, user_query: str):
    past = self.memory.search(user_query, n_results=2)
    if past:
        self.messages.append({"role": "system", "content": f"历史记忆：\n{''.join(past)}"})
    self.observe(user_query)
    # ... Think → Act ...
    self.memory.save(f"qa:{user_query[:20]}", f"Q: {user_query}\nA: {answer}", {"type": "qa"})
```

### 方式二：LLM 通过 Tool 决策（memory_tools_agent.py，推荐）

Memory 操作封装成 Tool，LLM 自行判断何时 save/update/delete/search：

```python
# LLM 输出 tool_call(name="memory_save", args={"key":"user_name","value":"小明"})
# → 代码执行 memory.save("user_name", "小明")
```

详见 `memory_tools_agent.py`。

## 文件结构

```
day03-memory/
├── README.md                  ← 本文件
├── memory.py                  ← Memory 类（ChromaDB 实现）
├── main.py                    ← 基本使用示例
├── agent_with_memory.py       ← Agent + Memory 集成（代码控制）
└── memory_tools_agent.py      ← Agent + Memory 集成（Tool 决策，推荐）
```
