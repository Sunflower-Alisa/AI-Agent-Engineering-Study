from agent import MinAgent
from tools import tool_definitions, tool_functions


def main():
    print("==== Mini Agent Tool Calling Demo (Day02) ====")
    agent = MinAgent(tools=tool_definitions, functions=tool_functions, max_steps=10)
    while True:
        query = input("\nUser: ")
        if query.lower() in ["exit", "quit"]:
            break

        answer = agent.run(query)
        print(f"Agent: {answer}")


if __name__ == "__main__":
    main()
