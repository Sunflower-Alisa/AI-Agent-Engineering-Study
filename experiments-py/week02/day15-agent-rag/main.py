import os
import sys

# 将本项目根目录加入 sys.path，便于使用绝对导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.agent import Agent
from agent.decision import Decision
from agent.evaluator import Evaluator
from agent.executor import Executor
from agent.planner import Planner
from agent.replanner import Replanner
from reflection.evaluator import Reflection_Evaluator
from reflection.improver import Improver
from generator import AnswerGenerator
from llm import chat
from actionrouter import ActionRouter


def main():
    # 构建知识库（加载 documents/agent.md → 切块 → 入库），供 knowledge_search 工具使用
    from rag.rag_pipeline import build_knowledge_base_from_project

    build_knowledge_base_from_project()

    planner = Planner()
    executor = Executor(chat)
    replanner = Replanner()
    evaluator = Evaluator()
    decision = Decision()
    reflection = Reflection_Evaluator()
    improver = Improver()
    generator = AnswerGenerator()
    router = ActionRouter()

    agent = Agent(
        planner,
        executor,
        replanner,
        evaluator,
        decision,
        generator,
        reflection,
        improver,
        router,
    )
    while True:
        query = input("\nUser: ")
        if query.lower() in ["exit", "quit"]:
            break

        answer = agent.run(query)
        print(f"Agent: {answer}")


if __name__ == "__main__":
    main()
