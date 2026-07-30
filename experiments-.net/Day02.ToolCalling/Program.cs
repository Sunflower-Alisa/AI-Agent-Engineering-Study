using AiAgent.Shared;
using Day02.ToolCalling;

var llm = new LlmClient();
var agent = new Agent(llm);

Console.WriteLine("Tool Calling Agent 启动 (输入 exit 退出)");
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
