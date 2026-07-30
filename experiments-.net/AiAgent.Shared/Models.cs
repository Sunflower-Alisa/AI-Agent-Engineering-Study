namespace AiAgent.Shared;

public class ChatMessage
{
    public string Role { get; set; } = "user";
    public string Content { get; set; } = "";
    public List<ToolCall>? ToolCalls { get; set; }
    public string? ToolCallId { get; set; }
}

public class ToolCall
{
    public string Id { get; set; } = "";
    public string FunctionName { get; set; } = "";
    public string FunctionArguments { get; set; } = "";
}

public class LlmResponse
{
    public string? Content { get; set; }
    public List<ToolCall>? ToolCalls { get; set; }
}

public class ToolDefinition
{
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public object Parameters { get; set; } = new { };
}

public class AgentState
{
    public string Goal { get; set; } = "";
    public List<string> Steps { get; set; } = new();
    public List<string> Completed { get; set; } = new();
    public List<string> Failed { get; set; } = new();
    public string? CurrentStep { get; set; }
}
