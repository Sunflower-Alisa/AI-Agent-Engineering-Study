using AiAgent.Shared;

namespace Day02.ToolCalling;

public static class Tools
{
    public static string Calculate(string expression)
    {
        try
        {
            var table = new System.Data.DataTable();
            return table.Compute(expression, "").ToString() ?? "";
        }
        catch
        {
            return $"无法计算: {expression}";
        }
    }

    public static string GetTime(string city)
    {
        var timezoneMap = new Dictionary<string, string>
        {
            ["北京"] = "Asia/Shanghai",
            ["上海"] = "Asia/Shanghai",
            ["纽约"] = "America/New_York",
            ["伦敦"] = "Europe/London",
            ["东京"] = "Asia/Tokyo",
            ["旧金山"] = "America/Los_Angeles",
        };

        if (!timezoneMap.ContainsKey(city))
            return $"暂不支持城市: {city}";

        var tz = TimeZoneInfo.FindSystemTimeZoneById(timezoneMap[city]);
        var now = TimeZoneInfo.ConvertTime(DateTime.UtcNow, tz);
        return now.ToString("yyyy-MM-dd HH:mm:ss");
    }

    public static List<ToolDefinition> Definitions => new()
    {
        new ToolDefinition
        {
            Name = "get_time",
            Description = "查询指定城市当前时间",
            Parameters = new
            {
                type = "object",
                properties = new
                {
                    city = new { type = "string", description = "城市名称" }
                },
                required = new[] { "city" }
            }
        },
        new ToolDefinition
        {
            Name = "calculate",
            Description = "数学表达式计算，传入算式字符串，例如 '1+2*3'",
            Parameters = new
            {
                type = "object",
                properties = new
                {
                    expression = new { type = "string", description = "数学表达式" }
                },
                required = new[] { "expression" }
            }
        }
    };

    public static Dictionary<string, Func<string, string>> Functions => new()
    {
        ["get_time"] = (args) =>
        {
            var json = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(args);
            return GetTime(json?["city"] ?? "");
        },
        ["calculate"] = (args) =>
        {
            var json = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(args);
            return Calculate(json?["expression"] ?? "");
        }
    };
}
