using AiAgent.Shared;

namespace Day04.Planning;

public class Replanner
{
    private readonly ILlmClient _llm;

    public Replanner(ILlmClient llm)
    {
        _llm = llm;
    }

    public void ReplanStatic(AgentState state, string reason)
    {
        Console.WriteLine($"重新规划原因：{reason}");
        state.Steps = new() { "学习LangGraph", "学习Tool Calling", "实现Agent项目" };
        state.Failed.Add(reason);
    }

    public async Task ReplanDynamic(AgentState state, string observation)
    {
        var prompt = $@"你是一个重新规划Agent,
当前目标：{state.Goal},
已经完成：{string.Join(", ", state.Completed)},
当前计划：{string.Join(", ", state.Steps)},
请重新指定下一步计划。
返回JSON:
{{
""steps"":[]
}}";

        var messages = new List<ChatMessage> { new() { Role = "user", Content = prompt } };
        var result = await _llm.ChatAsync(messages);

        try
        {
            var parsed = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, System.Text.Json.JsonElement>>(result);
            if (parsed != null && parsed.TryGetValue("steps", out var steps))
            {
                state.Steps = steps.EnumerateArray().Select(s => s.GetString() ?? "").ToList();
            }
        }
        catch { }
    }
}
