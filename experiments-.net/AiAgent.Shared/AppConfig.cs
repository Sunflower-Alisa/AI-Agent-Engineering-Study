namespace AiAgent.Shared;

public static class AppConfig
{
    public static string Provider { get; }
    public static string ApiKey { get; }
    public static string BaseUrl { get; }
    public static string Model { get; }

    static AppConfig()
    {
        Provider = Environment.GetEnvironmentVariable("LLM_PROVIDER") ?? "deepseek";
        var (baseUrl, envKey, model) = Provider switch
        {
            "openai" => ("https://api.openai.com/v1", "OPENAI_API_KEY", "gpt-4o-mini"),
            _ => ("https://api.deepseek.com", "DEEPSEEK_API_KEY", "deepseek-chat")
        };
        BaseUrl = baseUrl;
        Model = model;
        ApiKey = Environment.GetEnvironmentVariable(envKey)
            ?? throw new InvalidOperationException($"请设置 {envKey} 环境变量");
    }
}
