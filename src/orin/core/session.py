"""One bounded request-response cycle with a provider."""

from orin.core.agent import Agent, AgentOutcome
from orin.providers.base import AIProvider


def run_turn(provider: AIProvider, agent: Agent, message: str) -> AgentOutcome:
    first = provider.respond(message)
    outcome = agent.process(first)
    if not first.tool_calls:
        return outcome
    # Provider receives factual tool outputs; second-round tool calls are NOT executed.
    final = provider.respond(message, tool_results=outcome.results)
    return AgentOutcome(text=final.text, results=outcome.results)
