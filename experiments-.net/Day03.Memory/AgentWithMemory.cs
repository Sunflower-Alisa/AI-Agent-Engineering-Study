using AiAgent.Shared;

namespace Day03.Memory;

public class AgentWithMemory
{
    private readonly ILlmClient _llm;
    private readonly MemoryStore _memory;
    private readonly List<ChatMessage> _messages = new();

    public AgentWithMemory(ILlmClient llm, MemoryStore memory)
    {
        _llm = llm;
        _memory = memory;
    }

    public async Task<string> RunAsync(string userInput)
    {
        var relevant = _memory.Search(userInput, 3);
        if (relevant.Count > 0)
        {
            var context = string.Join("\n", relevant.Select(r => $"[{r.Id}] {r.Text}"));
            _messages.Add(new ChatMessage
            {
                Role = "system",
                Content = $"以下是相关的历史记忆:\n{context}"
            });
        }

        _messages.Add(new ChatMessage { Role = "user", Content = userInput });
        var response = await _llm.ChatAsync(_messages);
        _messages.Add(new ChatMessage { Role = "assistant", Content = response });

        _memory.Save(Guid.NewGuid().ToString("N")[..8], userInput, new() { ["response"] = response });

        return response;
    }
}
