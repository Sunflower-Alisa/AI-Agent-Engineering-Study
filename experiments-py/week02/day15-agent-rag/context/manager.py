class ContextManager:

    def build_context(self,user_input,history,memory,knowledge):
        context = f"""

用户问题:
{user_input}

历史对话:
{history}

用户长期记忆:
{memory}

知识库信息:
{knowledge}
"""

        return context
