using AiAgent.Shared;

namespace Day03.Memory;

public class MemoryToolAgent
{
    private readonly ILlmClient _llm;
    private readonly MemoryStore _memory;
    private readonly List<ChatMessage> _messages = new();
    private readonly int _maxSteps;

    public MemoryToolAgent(ILlmClient llm, MemoryStore memory, int maxSteps = 10)
    {
        _llm = llm;
        _memory = memory;
        _maxSteps = maxSteps;
    }

    public async Task<string> RunAsync(string userInput)
    {
        _messages.Add(new ChatMessage { Role = "user", Content = userInput });

        for (var i = 0; i < _maxSteps; i++)
        {
            var response = await _llm.ChatWithToolsAsync(_messages, MemoryTools);

            _messages.Add(new ChatMessage
            {
                Role = "assistant",
                Content = response.Content ?? "",
                ToolCalls = response.ToolCalls
            });

            if (response.ToolCalls == null || response.ToolCalls.Count == 0)
                return response.Content ?? "";

            foreach (var tc in response.ToolCalls)
            {
                Console.WriteLine($"  ▶ 记忆工具: {tc.FunctionName}({tc.FunctionArguments})");
                var result = ExecuteTool(tc.FunctionName, tc.FunctionArguments);
                _messages.Add(new ChatMessage { Role = "tool", ToolCallId = tc.Id, Content = result });
            }
        }

        return "达到最大执行轮次，任务停止";
    }

    private string ExecuteTool(string name, string args)
    {
        try
        {
            return name switch
            {
                "memory_save" => HandleSave(args),
                "memory_search" => HandleSearch(args),
                "memory_delete" => HandleDelete(args),
                "memory_count" => _memory.Count().ToString(),
                _ => $"未知工具: {name}"
            };
        }
        catch (Exception ex)
        {
            return $"工具执行错误: {ex.Message}";
        }
    }

    private string HandleSave(string args)
    {
        var json = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(args);
        var id = json!["id"];
        var text = json["text"];
        _memory.Save(id, text);
        return $"已保存记忆: {id}";
    }

    private string HandleSearch(string args)
    {
        var json = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(args);
        var query = json!["query"];
        var k = int.TryParse(json.GetValueOrDefault("k", "3"), out var n) ? n : 3;
        var results = _memory.Search(query, k);
        return results.Count == 0
            ? "未找到相关记忆"
            : string.Join("\n", results.Select(r => $"[{r.Id}] {r.Text}"));
    }

    private string HandleDelete(string args)
    {
        var json = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(args);
        var id = json!["id"];
        _memory.Delete(id);
        return $"已删除记忆: {id}";
    }

    private static List<ToolDefinition> MemoryTools => new()
    {
        new ToolDefinition
        {
            Name = "memory_save",
            Description = "保存一条记忆",
            Parameters = new
            {
                type = "object",
                properties = new
                {
                    id = new { type = "string", description = "记忆 ID" },
                    text = new { type = "string", description = "记忆内容" }
                },
                required = new[] { "id", "text" }
            }
        },
        new ToolDefinition
        {
            Name = "memory_search",
            Description = "搜索相关记忆",
            Parameters = new
            {
                type = "object",
                properties = new
                {
                    query = new { type = "string", description = "搜索关键词" },
                    k = new { type = "integer", description = "返回数量" }
                },
                required = new[] { "query" }
            }
        },
        new ToolDefinition
        {
            Name = "memory_delete",
            Description = "删除指定记忆",
            Parameters = new
            {
                type = "object",
                properties = new
                {
                    id = new { type = "string", description = "记忆 ID" }
                },
                required = new[] { "id" }
            }
        },
        new ToolDefinition
        {
            Name = "memory_count",
            Description = "获取记忆总数",
            Parameters = new { type = "object", properties = new { }, required = Array.Empty<string>() }
        }
    };
}
