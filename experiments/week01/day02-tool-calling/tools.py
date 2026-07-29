from zoneinfo import ZoneInfo
from datetime import datetime


def calculate(expression):
    return eval(expression)


def get_time(city):
    timezone_map = {
        "北京": "Asia/Shanghai",
        "上海": "Asia/Shanghai",
        "纽约": "America/New_York",
        "伦敦": "Europe/London",
        "东京": "Asia/Tokyo",
        "旧金山": "America/Los_Angeles",
    }

    if city not in timezone_map:
        return f"暂不支持城市：{city}"

    tz = ZoneInfo(timezone_map[city])

    now = datetime.now(tz)

    return now.strftime("%Y-%m-%d %H:%M:%S")


tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "查询指定城市当前时间",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名称"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "数学表达式计算，传入算式字符串，例如'1+2*3'",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"],
            },
        },
    },
]

tool_functions = {"get_time": get_time, "calculate": calculate}
