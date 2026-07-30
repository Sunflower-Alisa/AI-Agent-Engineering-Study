using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace AiAgent.Shared;

public class LlmClient : ILlmClient
{
    private readonly HttpClient _http = new();
    private readonly string _baseUrl;
    private readonly string _model;
    private readonly string _apiKey;

    public LlmClient()
    {
        _baseUrl = AppConfig.BaseUrl.TrimEnd('/');
        _model = AppConfig.Model;
        _apiKey = AppConfig.ApiKey;
    }

    public async Task<string> ChatAsync(List<ChatMessage> messages)
    {
        var dtoMessages = messages.Select(ToDto).ToList();
        var body = new ChatCompletionRequest { Model = _model, Messages = dtoMessages };
        var doc = await PostAsync(body);
        return doc.RootElement
            .GetProperty("choices")[0]
            .GetProperty("message")
            .GetProperty("content")
            .GetString() ?? "";
    }

    public async Task<LlmResponse> ChatWithToolsAsync(List<ChatMessage> messages, List<ToolDefinition>? tools)
    {
        var dtoMessages = messages.Select(ToDto).ToList();
        var body = new ChatCompletionRequest
        {
            Model = _model,
            Messages = dtoMessages,
            Tools = tools?.Select(ToToolDto).ToList()
        };
        var doc = await PostAsync(body);
        var msg = doc.RootElement.GetProperty("choices")[0].GetProperty("message");

        var content = msg.TryGetProperty("content", out var c) ? c.GetString() : null;

        List<ToolCall>? toolCalls = null;
        if (msg.TryGetProperty("tool_calls", out var tc))
        {
            toolCalls = tc.EnumerateArray().Select(t => new ToolCall
            {
                Id = t.GetProperty("id").GetString() ?? "",
                FunctionName = t.GetProperty("function").GetProperty("name").GetString() ?? "",
                FunctionArguments = t.GetProperty("function").GetProperty("arguments").GetString() ?? "",
            }).ToList();
        }

        return new LlmResponse { Content = content, ToolCalls = toolCalls };
    }

    private async Task<JsonDocument> PostAsync(ChatCompletionRequest body)
    {
        var json = JsonSerializer.Serialize(body);
        var httpContent = new StringContent(json, Encoding.UTF8, "application/json");
        var request = new HttpRequestMessage(HttpMethod.Post, $"{_baseUrl}/chat/completions");
        request.Headers.Add("Authorization", $"Bearer {_apiKey}");
        request.Content = httpContent;

        var response = await _http.SendAsync(request);
        response.EnsureSuccessStatusCode();
        var responseBody = await response.Content.ReadAsStringAsync();
        return JsonDocument.Parse(responseBody);
    }

    private static ChatMessageDto ToDto(ChatMessage m) => new()
    {
        Role = m.Role,
        Content = m.Content,
        ToolCallId = m.ToolCallId,
        ToolCalls = m.ToolCalls?.Select(tc => new ToolCallDto
        {
            Id = tc.Id,
            Function = new FunctionCallDto
            {
                Name = tc.FunctionName,
                Arguments = tc.FunctionArguments
            }
        }).ToList()
    };

    private static ToolDefinitionDto ToToolDto(ToolDefinition t) => new()
    {
        Type = "function",
        Function = new FunctionDef
        {
            Name = t.Name,
            Description = t.Description,
            Parameters = t.Parameters
        }
    };
}

#region Internal DTOs (OpenAI-compatible API format)

internal class ChatCompletionRequest
{
    [JsonPropertyName("model")] 
    public string Model { get; set; } = "";
    [JsonPropertyName("messages")] 
    public List<ChatMessageDto> 
    Messages { get; set; } = new();
    [JsonPropertyName("tools"), JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public List<ToolDefinitionDto>? Tools { get; set; }
}

internal class ChatMessageDto
{
    [JsonPropertyName("role")]
    public string Role { get; set; } = "";
    [JsonPropertyName("content")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? Content { get; set; }
    [JsonPropertyName("tool_calls"), JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public List<ToolCallDto>? ToolCalls { get; set; }
    [JsonPropertyName("tool_call_id"), JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? ToolCallId { get; set; }
}

internal class ToolCallDto
{
    [JsonPropertyName("id")] public string Id { get; set; } = "";
    [JsonPropertyName("type")] public string Type { get; set; } = "function";
    [JsonPropertyName("function")] public FunctionCallDto Function { get; set; } = new();
}

internal class FunctionCallDto
{
    [JsonPropertyName("name")] public string Name { get; set; } = "";
    [JsonPropertyName("arguments")] public string Arguments { get; set; } = "";
}

internal class ToolDefinitionDto
{
    [JsonPropertyName("type")] 
    public string Type { get; set; } = "function";
    [JsonPropertyName("function")] 
    public FunctionDef Function { get; set; } = new();
}

internal class FunctionDef
{
    [JsonPropertyName("name")] 
    public string Name { get; set; } = "";
    [JsonPropertyName("description")] 
    public string Description { get; set; } = "";
    [JsonPropertyName("parameters")] 
    public object Parameters { get; set; } = new { };
}

#endregion
