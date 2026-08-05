class AgentState:
    def __init__(self, goal):
        self.goal = goal
        self.steps = []
        self.completed = []
        self.failed = []
        self.current_step = None
        self.observation = None  # 当前动作的观察结果（LLM每次决策能读到）
        self.observations = []  # 历史观察/工具结果记录
        self.next_action = None
        self.evaluation = None
        self.tool_results = {}  # 工具结果缓存：(name, args) → 结果，避免重复计算
        self.final_answer = None
