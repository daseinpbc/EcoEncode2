# main_agentos.py

import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

# Replace with your agent JWT
AGENT_JWT = ""  # TODO: Add your agent JWT here
session = GenAISession(jwt_token=AGENT_JWT)


@session.bind(
    name="full_stack_agent",
    description="Full stack agent that plans, executes, and audits React code for sustainability."
)
async def full_stack_agent(
    agent_context: GenAIContext,
    prompt: Annotated[
        str,
        "User prompt for planning and code generation."
    ]
) -> dict:
    """
    Accepts a prompt, plans, generates code, and audits for eco-grade.
    """
    # Example: You can call other agents/tools here if needed
    # For now, just echo the prompt and a dummy result
    return {
        "generatedCode": f"// React code for: {prompt}",
        "reportMarkdown": "Eco-Grade: 100\nAll best practices applied.",
        "ecoGrade": 100
    }


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
