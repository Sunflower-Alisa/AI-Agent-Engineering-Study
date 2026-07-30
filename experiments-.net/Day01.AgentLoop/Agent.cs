using AiAgent.Shared;

namespace Day01.AgentLoop;

public class Agent
{
    private readonly ILlmClient _llm;
    private readonly Dictionary<string, Func<string>> _tools;

    public Agent(ILlmClient llm, Dictionary<string, Func<string>> tools)
    {
        _llm = llm;
        _tools = tools;
    }

    private int _maxSteps = 20;

    public async Task<string> RunAsync(string userInput)
    {
        var systemPrompt = $@"你是一个智能助手，你可以使用以下工具：
{string.Join("\n", _tools.Keys.Select(t => $"- {t}"))}

请以 JSON 格式回复：
- 如果需要调用工具，返回 {{""action"": ""工具名"", ""answer"": null}}
- 如果可以直接回答，返回 {{""action"": null, ""answer"": ""你的回答""}}";

        var messages = new List<ChatMessage>
        {
            new() { Role = "system", Content = systemPrompt },
            new() { Role = "user", Content = userInput }
        };

        for (var step = 0; step < _maxSteps; step++)
        {
            var response = await _llm.ChatAsync(messages);

            try
            {
                var parsed = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, object?>>(response);
                var action = parsed?.GetValueOrDefault("action")?.ToString();

                if (!string.IsNullOrEmpty(action) && _tools.ContainsKey(action))
                {
                    Console.WriteLine($"  ▶ 调用工具: {action}");
                    var result = _tools[action]();
                    messages.Add(new ChatMessage { Role = "assistant", Content = response });
                    messages.Add(new ChatMessage { Role = "user", Content = $"工具 {action} 返回: {result}" });
                }
                else
                {
                    return parsed?.GetValueOrDefault("answer")?.ToString() ?? response;
                }
            }
            catch
            {
                return response;
            }
        }

        return "达到最大执行轮次，停止";
    }
}
