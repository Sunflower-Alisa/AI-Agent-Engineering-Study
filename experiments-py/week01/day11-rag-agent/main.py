from pathlib import Path

from rag.llm import chat
from rag.rag_pipeline import build_knowledge_base, retrieve_context

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    doc_path = str(base_dir / "documents" / "agent.md")
    # 1. 第一次运行执行构建知识库（后续可注释，避免重复入库）
    build_knowledge_base(doc_path)

    # 2. 用户提问，检索相关知识
    user_question = "AI Agent包含哪些核心模块？"
    context = retrieve_context(user_question)

    print("=" * 50)
    print(f"用户问题：{user_question}")
    print("【检索到的参考上下文】")
    print(context)

    # 3. 拼接 Prompt 送入 LLM 生成最终答案
    prompt_template = """
基于下面提供的参考资料回答用户问题，只使用资料里的内容，不要编造。
参考资料：
{context}

用户问题：{question}
你的回答：
"""
    final_prompt = prompt_template.format(context=context, question=user_question)
    print("\n【组装完成送入LLM的Prompt】")
    print(final_prompt)

    answer = chat(final_prompt)
    print("=" * 50)
    print("【Agent 最终回答】")
    print(answer)
