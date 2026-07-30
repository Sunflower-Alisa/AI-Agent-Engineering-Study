class AgentState:
    def __init__(self,goal):
        self.goal = goal
        self.steps = []
        self.completed = []
        self.failed = []
        self.current_step = None
        self.observations = []



