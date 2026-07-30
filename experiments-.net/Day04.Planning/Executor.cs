namespace Day04.Planning;

public class Executor
{
    public (bool success, string? reason) ExecuteStep(string step)
    {
        Console.WriteLine($"执行：{step}");

        if (step == "学习LangChain")
        {
            return (false, "发现LangGraph更适合作为Agent框架");
        }

        return (true, null);
    }
}
