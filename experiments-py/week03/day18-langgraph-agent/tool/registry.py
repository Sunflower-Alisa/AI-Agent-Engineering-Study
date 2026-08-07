TOOLS = {}

def register(tool):
    TOOLS[tool.name] = tool

def get_tool(name):
    return TOOLS.get(name)

def get_all_tools():
    return TOOLS