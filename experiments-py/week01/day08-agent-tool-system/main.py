from planner import Planner
from executor import Executor
from replanner import Replanner
from evaluator import Evaluator
from decision import Decision
from agent import Agent


def main():
    planner = Planner()
    executor = Executor()
    replanner = Replanner()
    evaluator = Evaluator()
    decision = Decision()

    agent = Agent(planner, executor, replanner, evaluator, decision)
    while True:
        query = input("\nUser: ")
        if query.lower() in ["exit", "quit"]:
            break

        answer = agent.run(query)
        print(f"Agent: {answer}")


if __name__ == "__main__":
    main()
