namespace AiAgent.Shared;

public interface ILlmClient
{
    Task<string> ChatAsync(List<ChatMessage> messages);
    Task<LlmResponse> ChatWithToolsAsync(List<ChatMessage> messages, List<ToolDefinition>? tools);
}
