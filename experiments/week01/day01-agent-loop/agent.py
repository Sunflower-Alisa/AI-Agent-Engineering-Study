class Agent:
    def __init__(self,llm,tools):
        self.llm = llm
        self.tools = tools

    def run(self,input):
        while True:
            response = self.llm(input)

            if response["action"]:
                result = self.tools[response["action"]]()
                input = result

            else:
                return response["answer"]