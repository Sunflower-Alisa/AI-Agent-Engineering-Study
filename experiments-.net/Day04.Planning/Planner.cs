using AiAgent.Shared;

namespace Day04.Planning;

public class Planner
{
    private readonly ILlmClient _llm;

    public Planner(ILlmClient llm)
    {
        _llm = llm;
    }

    public List<string> CreatePlanStatic(string goal)
    {
        if (goal.Contains("AI Agent"))
        {
            return new()
            {
                "理解Agent基础",
                "学习Agent Loop",
                "学习LangChain",
                "学习Tool Calling",
                "学习Memory",
                "实现RAG Agent"
            };
        }
        return new() { "分析目标", "制定步骤" };
    }

    public async Task<List<string>> CreatePlanDynamic(string goal)
    {
        var prompt = $@"你是一个任务规划Agent，用户目标：{goal},请拆解成可执行步骤。
要求返回JSON:
{{
""steps"":[
""步骤1"",
""步骤2"",
""步骤3""
]}}
不要输出其他内容。";

        var messages = new List<ChatMessage> { new() { Role = "user", Content = prompt } };
        var result = await _llm.ChatAsync(messages);

        try
        {
            var parsed = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, System.Text.Json.JsonElement>>(result);
            if (parsed != null && parsed.TryGetValue("steps", out var steps))
            {
                return steps.EnumerateArray().Select(s => s.GetString() ?? "").ToList();
            }
        }
        catch { }

        return new() { "分析目标", "制定步骤" };
    }
}
