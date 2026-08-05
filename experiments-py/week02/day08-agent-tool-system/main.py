from .planner import Planner
from .executor import Executor
from .replanner import Replanner
from .evaluator import Evaluator
from .decision import Decision
from .agent import Agent
from .reflection.evaluator import Reflection_Evaluator
from .reflection.improver import Improver
from .generator import AnswerGenerator
from .llm import chat
from .actionrouter import ActionRouter


def main():
    planner = Planner()
    executor = Executor(chat)
    replanner = Replanner()
    evaluator = Evaluator()
    decision = Decision()
    # Day9 新增
    reflection = Reflection_Evaluator()
    improver = Improver()
    generator = AnswerGenerator()
    router = ActionRouter()

    agent = Agent(planner, executor, replanner, evaluator, decision,generator,reflection,improver,router)
    while True:
        query = input("\nUser: ")
        if query.lower() in ["exit", "quit"]:
            break

        answer = agent.run(query)
        print(f"Agent: {answer}")


if __name__ == "__main__":
    main()
