from models import Evaluation


class Evaluator:
    # 用途：判断结果质量
    def evaluate(self, state, observation):
        if observation.issues:
            return Evaluation(need_replan=True, reason=observation.issues)

        return Evaluation(success=True, need_replan=False)
