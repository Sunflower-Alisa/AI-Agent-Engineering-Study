using AiAgent.Shared;
using Day03.Memory;

var llm = new LlmClient();
var memory = new MemoryStore();

Console.WriteLine("=== Day03 Memory Agent ===");
Console.WriteLine("请选择模式:");
Console.WriteLine("1. 代码控制型 AgentWithMemory (自动保存/检索记忆)");
Console.WriteLine("2. Tool 决策型 MemoryToolAgent (LLM 决定何时操作记忆)");
Console.Write("选择 (1/2): ");
var choice = Console.ReadLine();

if (choice == "2")
{
    var agent = new MemoryToolAgent(llm, memory);
    Console.WriteLine("MemoryToolAgent 启动 (输入 exit 退出)");
    Console.Write("你: ");
    var input = Console.ReadLine();
    while (input is not null and not "" and not "exit")
    {
        var result = await agent.RunAsync(input);
        Console.WriteLine($"Agent: {result}");
        Console.WriteLine();
        Console.Write("你: ");
        input = Console.ReadLine();
    }
}
else
{
    var agent = new AgentWithMemory(llm, memory);
    Console.WriteLine("AgentWithMemory 启动 (输入 exit 退出)");
    Console.Write("你: ");
    var input = Console.ReadLine();
    while (input is not null and not "" and not "exit")
    {
        var result = await agent.RunAsync(input);
        Console.WriteLine($"Agent: {result}");
        Console.WriteLine();
        Console.Write("你: ");
        input = Console.ReadLine();
    }
}
