#A2a_server for possible extra functionality

import asyncio
import uvicorn
from a2a.server.app import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.task_store import InMemoryTaskStore
from a2a.server.agent_executors import AgentExecutor
from a2a.types.agent_card import AgentCard, AgentSkill, AgentCapabilities
from a2a.types.content import ContentType, ContentMode

# Import your agents from main_multi_agent.py
from main_multi_agent import (
    planner_agent,
    executor_agent,
    auditor_agent,
    full_stack_agent,
)

# A dummy GenAIContext class to pass to the agent functions
class DummyGenAIContext:
    pass

class SingleAgentExecutor(AgentExecutor):
    """
    An agent executor that invokes a single, specific agent function.
    """
    SUPPORTED_CONTENT_TYPES = [ContentType.TEXT_PLAIN]

    def __init__(self, agent_func, is_plan_based=False):
        self.agent_func = agent_func
        self.is_plan_based = is_plan_based
        self.agent_context = DummyGenAIContext()

    async def invoke(self, content: str, skill_id: str) -> str:
        """
        Invoke the agent function with the appropriate arguments.
        """
        import json
        try:
            if self.is_plan_based:
                plan = json.loads(content)
                result = await self.agent_func(self.agent_context, plan=plan)
            else:
                result = await self.agent_func(self.agent_context, user_request=content)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

def create_a2a_server(agent_func, skill, url, is_plan_based=False):
    """
    Creates and configures an A2AStarletteApplication for a single agent.
    """
    card = AgentCard(
        name=skill.name,
        description=skill.description,
        url=url,
        version="1.0.0",
        defaultInputModes=[ContentMode.TEXT_PLAIN],
        defaultOutputModes=[ContentMode.TEXT_PLAIN],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill]
    )

    request_handler = DefaultRequestHandler(
        agent_executor=SingleAgentExecutor(agent_func, is_plan_based),
        task_store=InMemoryTaskStore(),
    )

    return A2AStarletteApplication(agent_card=card, http_handler=request_handler)

async def run_server(app, host, port):
    """
    Runs a Uvicorn server for a given application.
    """
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """
    Creates and runs the four A2A agent servers concurrently.
    """
    planner_skill = AgentSkill(
        id="planner_agent", name="Planner Agent",
        description="Analyzes a user's request and creates a sustainable coding plan."
    )
    executor_skill = AgentSkill(
        id="executor_agent", name="Executor Agent",
        description="Generates React code based on a provided JSON plan."
    )
    auditor_skill = AgentSkill(
        id="auditor_agent", name="Auditor Agent",
        description="Calculates an Eco-Grade based on a provided JSON plan."
    )
    full_stack_skill = AgentSkill(
        id="full_stack_agent", name="Full Stack Agent",
        description="Orchestrates the planning, execution, and auditing of sustainable code generation."
    )

    # --- CHANGES ---
    # Create the four server applications with the corrected docker host URL
    planner_app = create_a2a_server(
        planner_agent, planner_skill, "http://host.docker.internal:9001/"
    )
    executor_app = create_a2a_server(
        executor_agent, executor_skill, "http://host.docker.internal:9002/", is_plan_based=True
    )
    auditor_app = create_a2a_server(
        auditor_agent, auditor_skill, "http://host.docker.internal:9003/", is_plan_based=True
    )
    full_stack_app = create_a2a_server(
        full_stack_agent, full_stack_skill, "http://host.docker.internal:9004/"
    )

    print("Starting 4 A2A Agent Servers...")
    print("Planner Agent URL: http://host.docker.internal:9001")
    print("Executor Agent URL: http://host.docker.internal:9002")
    print("Auditor Agent URL: http://host.docker.internal:9003")
    print("Full Stack Agent URL: http://host.docker.internal:9004")
    print("-" * 50)

    # Run all servers concurrently
    await asyncio.gather(
        run_server(planner_app.build(), "0.0.0.0", 9001),
        run_server(executor_app.build(), "0.0.0.0", 9002),
        run_server(auditor_app.build(), "0.0.0.0", 9003),
        run_server(full_stack_app.build(), "0.0.0.0", 9004),
    )

if __name__ == "__main__":
    asyncio.run(main())
