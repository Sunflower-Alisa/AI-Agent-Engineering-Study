using AiAgent.Shared;
using Day01.AgentLoop;

var tools = new Dictionary<string, Func<string>>
{
    ["get_current_time"] = () => DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
    ["roll_dice"] = () => Random.Shared.Next(1, 7).ToString(),
};

var llm = new LlmClient();
var agent = new Agent(llm, tools);

Console.WriteLine("Agent 启动 (输入 exit 退出)");
Console.Write("你: ");
var input = Console.ReadLine() ?? "";

while (input is not null and not "" and not "exit")
{
    var result = await agent.RunAsync(input);
    Console.WriteLine($"Agent: {result}");
    Console.WriteLine();
    Console.Write("你: ");
    input = Console.ReadLine();
}
