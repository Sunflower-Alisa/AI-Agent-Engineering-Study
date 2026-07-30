using AiAgent.Shared;

namespace Day02.ToolCalling;

public class Agent
{
    private readonly ILlmClient _llm;
    private readonly List<ChatMessage> _messages = new();
    private readonly int _maxSteps;

    public Agent(ILlmClient llm, int maxSteps = 10)
    {
        _llm = llm;
        _maxSteps = maxSteps;
    }

    public void Observe(string userInput)
    {
        _messages.Add(new ChatMessage { Role = "user", Content = userInput });
    }

    public async Task<string> RunAsync(string userQuery)
    {
        Observe(userQuery);

        for (var i = 0; i < _maxSteps; i++)
        {
            var response = await _llm.ChatWithToolsAsync(_messages, Tools.Definitions);

            _messages.Add(new ChatMessage
            {
                Role = "assistant",
                Content = response.Content ?? "",
                ToolCalls = response.ToolCalls
            });

            if (response.ToolCalls == null || response.ToolCalls.Count == 0)
                return response.Content ?? "";

            foreach (var toolCall in response.ToolCalls)
            {
                Console.WriteLine($"  ▶ 调用工具: {toolCall.FunctionName}({toolCall.FunctionArguments})");

                if (Tools.Functions.TryGetValue(toolCall.FunctionName, out var func))
                {
                    var result = func(toolCall.FunctionArguments);
                    _messages.Add(new ChatMessage
                    {
                        Role = "tool",
                        ToolCallId = toolCall.Id,
                        Content = result
                    });
                }
            }
        }

        return "达到最大执行轮次，任务停止";
    }
}
