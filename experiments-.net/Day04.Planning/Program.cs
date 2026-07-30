using AiAgent.Shared;
using Day04.Planning;

var llm = new LlmClient();
var planner = new Planner(llm);
var executor = new Executor();
var evaluator = new Evaluator();
var replanner = new Replanner(llm);

var goal = "帮我制定学习AI Agent路线";
var state = new AgentState { Goal = goal };

state.Steps = await planner.CreatePlanDynamic(goal);

while (state.Steps.Count > 0)
{
    var step = state.Steps[0];
    state.Steps.RemoveAt(0);
    state.CurrentStep = step;

    var (success, reason) = executor.ExecuteStep(step);

    var (needReplan, evalReason) = evaluator.Evaluate(state, success ? null : reason);

    if (needReplan)
    {
        await replanner.ReplanDynamic(state, evalReason!);
    }
    else
    {
        state.Completed.Add(step);
    }
}

Console.WriteLine($"目标：{state.Goal}");
Console.WriteLine($"\n计划：");
foreach (var step in state.Steps)
    Console.WriteLine($"  . {step}");

Console.WriteLine($"\n计划完成：{string.Join(", ", state.Completed)}");
Console.WriteLine($"计划失败：{string.Join(", ", state.Failed)}");
