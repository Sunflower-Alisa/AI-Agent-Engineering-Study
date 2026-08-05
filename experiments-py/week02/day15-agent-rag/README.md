## RAG在Agent中的位置。
RAG不是每次都执行，而是一种Agent能力。也可以当做一种工具，帮助获取知识的工具

                User
                 |
                 ↓
             Decision
                 |
        判断是否需要知识
                 |
        -----------------
        |               |
       Tool            RAG
        |               |
    Calculator     Knowledge Search


## Agent调用RAG完整流程
    用户
    "什么是Agent Loop？"
        ↓
    Agent Decision
        ↓
    判断：
    需要知识？
        ↓
    调用：
    knowledge_search
        ↓
    Retriever
        ↓
    VectorDB
        ↓
    返回相关Chunk
        ↓
    加入Context
        ↓
    LLM生成答案

## 1. 为什么RAG适合作为Agent Tool？

答案：因为RAG是一种外部知识获取能力，Agent应该根据任务需要决定是否调用，而不是固定执行。

## 2. RAG和普通Search Tool有什么区别？

Search：互联网信息
RAG：私有知识库

## 3. 为什么Decision需要知道knowledge_search？

因为：Decision负责选择下一步行动。
如果不知道：Agent无法主动使用知识库。

