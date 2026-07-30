using AiAgent.Shared;

namespace Day04.Planning;

public class Evaluator
{
    public (bool needReplan, string? reason) Evaluate(AgentState state, string? observation)
    {
        if (!string.IsNullOrEmpty(observation))
        {
            return (true, observation);
        }
        return (false, null);
    }
}
