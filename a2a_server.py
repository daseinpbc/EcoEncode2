#A2a_server for possible extra functionality
import os
import sys
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to Python path to enable imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
logger.info(f"Adding project root to path: {project_root}")
sys.path.append(project_root)

# Import repository-specific modules
try:
    from src.repositories.a2a import a2a_repo
    from src.repositories.agent import agent_repo
    from src.schemas.api.a2a.schemas import A2AAgentCard, A2AAgentSkill, A2AAgentCapabilities
    from src.schemas.api.a2a.enums import ContentMode, ContentType
    from src.schemas.mcp.schemas import MCPMessage, MCPMessageContent, MCPContentType
    from src.core.settings import get_settings
    from src.utils.a2a.server import A2AServer, A2ARequestHandler, A2AAgentExecutor
    from src.utils.mcp.server import MCPServer, MCPRequestHandler
    logger.info("Successfully imported repository modules")
except ImportError as e:
    logger.error(f"Failed to import repository modules: {e}")
    raise

# Import your agents from the main_multi_agent module
try:
    from main_multi_agent import (
        planner_agent,
        executor_agent,
        auditor_agent,
        full_stack_agent,
        GenAIContext
    )
    logger.info("Successfully imported agents from main_multi_agent")
except ImportError as e:
    logger.error(f"Failed to import agents: {e}")
    raise

# Get settings
settings = get_settings()

class GenAIAgentExecutor(A2AAgentExecutor):
    """
    Custom agent executor that adapts our agent functions to the A2A protocol.
    """
    def __init__(self, agent_func, context=None):
        self.agent_func = agent_func
        self.context = context or GenAIContext()
        
    async def execute(self, content, skill_id, content_type=ContentType.TEXT_PLAIN):
        """
        Execute the agent function with the given content.
        """
        try:
            logger.info(f"Executing agent {skill_id} with content type {content_type}")
            
            # Handle different content types
            if content_type == ContentType.APPLICATION_JSON:
                if skill_id == "planner_agent":
                    result = await planner_agent(self.context, content.get("user_request", ""))
                elif skill_id == "executor_agent":
                    result = await executor_agent(self.context, content)
                elif skill_id == "auditor_agent":
                    result = await auditor_agent(self.context, content)
                elif skill_id == "full_stack_agent":
                    result = await full_stack_agent(self.context, content.get("prompt", ""))
                else:
                    logger.error(f"Unknown skill ID: {skill_id}")
                    return {"error": f"Unknown skill ID: {skill_id}"}
            else:  # Assume plain text
                if skill_id == "planner_agent":
                    result = await planner_agent(self.context, content)
                elif skill_id == "full_stack_agent":
                    result = await full_stack_agent(self.context, content)
                else:
                    logger.error(f"Skill {skill_id} requires JSON input")
                    return {"error": f"Skill {skill_id} requires JSON input"}
                    
            return result
        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return {"error": str(e)}

class MCPAgentExecutor:
    """
    Executor for handling MCP messages and forwarding them to the appropriate agent.
    """
    def __init__(self, agent_func, context=None):
        self.agent_func = agent_func
        self.context = context or GenAIContext()
        
    async def execute_message(self, message: MCPMessage) -> MCPMessage:
        """
        Execute the agent function based on an MCP message.
        """
        try:
            logger.info(f"Executing MCP message: {message}")
            
            # Extract content from the message
            content = message.content
            skill_id = message.metadata.get("skill_id", "default_skill")
            
            # Process the content based on its type
            if content.type == MCPContentType.TEXT:
                text_content = content.content
                
                # Route to the appropriate agent
                if skill_id == "planner_agent":
                    result = await planner_agent(self.context, text_content)
                elif skill_id == "executor_agent":
                    # For executor, try to parse JSON if possible
                    try:
                        json_content = json.loads(text_content)
                        result = await executor_agent(self.context, json_content)
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON for executor agent")
                        return MCPMessage(
                            id=str(uuid4()),
                            content=MCPMessageContent(
                                type=MCPContentType.TEXT,
                                content=json.dumps({"error": "Invalid JSON input"})
                            ),
                            metadata={"error": "Invalid JSON input"}
                        )
                elif skill_id == "auditor_agent":
                    # For auditor, try to parse JSON if possible
                    try:
                        json_content = json.loads(text_content)
                        result = await auditor_agent(self.context, json_content)
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON for auditor agent")
                        return MCPMessage(
                            id=str(uuid4()),
                            content=MCPMessageContent(
                                type=MCPContentType.TEXT,
                                content=json.dumps({"error": "Invalid JSON input"})
                            ),
                            metadata={"error": "Invalid JSON input"}
                        )
                elif skill_id == "full_stack_agent":
                    result = await full_stack_agent(self.context, text_content)
                else:
                    logger.error(f"Unknown skill ID in MCP message: {skill_id}")
                    return MCPMessage(
                        id=str(uuid4()),
                        content=MCPMessageContent(
                            type=MCPContentType.TEXT,
                            content=json.dumps({"error": f"Unknown skill ID: {skill_id}"})
                        ),
                        metadata={"error": f"Unknown skill ID: {skill_id}"}
                    )
                
                # Return the result as an MCP message
                return MCPMessage(
                    id=str(uuid4()),
                    content=MCPMessageContent(
                        type=MCPContentType.TEXT,
                        content=json.dumps(result) if isinstance(result, dict) else str(result)
                    ),
                    metadata={"skill_id": skill_id}
                )
            elif content.type == MCPContentType.JSON:
                # Handle JSON content
                json_content = content.content
                
                # Route to the appropriate agent
                if skill_id == "planner_agent":
                    result = await planner_agent(self.context, json_content.get("user_request", ""))
                elif skill_id == "executor_agent":
                    result = await executor_agent(self.context, json_content)
                elif skill_id == "auditor_agent":
                    result = await auditor_agent(self.context, json_content)
                elif skill_id == "full_stack_agent":
                    result = await full_stack_agent(self.context, json_content.get("prompt", ""))
                else:
                    logger.error(f"Unknown skill ID in MCP message: {skill_id}")
                    return MCPMessage(
                        id=str(uuid4()),
                        content=MCPMessageContent(
                            type=MCPContentType.JSON,
                            content={"error": f"Unknown skill ID: {skill_id}"}
                        ),
                        metadata={"error": f"Unknown skill ID: {skill_id}"}
                    )
                
                # Return the result as an MCP message
                return MCPMessage(
                    id=str(uuid4()),
                    content=MCPMessageContent(
                        type=MCPContentType.JSON,
                        content=result
                    ),
                    metadata={"skill_id": skill_id}
                )
            else:
                logger.error(f"Unsupported MCP content type: {content.type}")
                return MCPMessage(
                    id=str(uuid4()),
                    content=MCPMessageContent(
                        type=MCPContentType.TEXT,
                        content=json.dumps({"error": f"Unsupported content type: {content.type}"})
                    ),
                    metadata={"error": f"Unsupported content type: {content.type}"}
                )
        except Exception as e:
            logger.error(f"Error executing MCP message: {e}")
            return MCPMessage(
                id=str(uuid4()),
                content=MCPMessageContent(
                    type=MCPContentType.TEXT,
                    content=json.dumps({"error": str(e)})
                ),
                metadata={"error": str(e)}
            )

class GenAIMCPRequestHandler(MCPRequestHandler):
    """
    Custom MCP request handler for GenAI agents.
    """
    def __init__(self, executor: MCPAgentExecutor):
        self.executor = executor
        
    async def handle_message(self, message: MCPMessage) -> MCPMessage:
        """
        Handle an incoming MCP message.
        """
        return await self.executor.execute_message(message)

def create_a2a_server_with_mcp(agent_func, skill, base_url, supports_json_input=False):
    """
    Create an A2A server with MCP support for a specific agent.
    
    Args:
        agent_func: The agent function
        skill: The A2AAgentSkill for the agent
        base_url: The base URL for the agent
        supports_json_input: Whether the agent supports JSON input
        
    Returns:
        A tuple of (A2AServer, MCPServer)
    """
    # Create agent card
    card = A2AAgentCard(
        name=skill.name,
        description=skill.description,
        url=base_url,
        version="1.0.0",
        defaultInputModes=[ContentMode.TEXT_PLAIN] if not supports_json_input else [ContentMode.JSON],
        defaultOutputModes=[ContentMode.JSON],
        capabilities=A2AAgentCapabilities(streaming=False, mcp=True),  # Enable MCP capability
        skills=[skill]
    )
    
    # Create A2A executor and request handler
    a2a_executor = GenAIAgentExecutor(agent_func)
    a2a_handler = A2ARequestHandler(executor=a2a_executor)
    
    # Create MCP executor and request handler
    mcp_executor = MCPAgentExecutor(agent_func)
    mcp_handler = GenAIMCPRequestHandler(executor=mcp_executor)
    
    # Create A2A server
    a2a_server = A2AServer(agent_card=card, request_handler=a2a_handler)
    
    # Create MCP server
    mcp_server = MCPServer(handler=mcp_handler)
    
    # Register MCP server with A2A server
    a2a_server.register_mcp_server(mcp_server)
    
    return a2a_server

async def main():
    """
    Main function to start all A2A servers with MCP support.
    """
    # Define skills for each agent
    planner_skill = A2AAgentSkill(
        id="planner_agent",
        name="Sustainable Planning Agent",
        description="Creates sustainable coding plans for React components",
        tags=["planning", "sustainability"]
    )
    
    executor_skill = A2AAgentSkill(
        id="executor_agent",
        name="Code Execution Agent",
        description="Generates React code based on sustainable plans",
        tags=["react", "code-generation"]
    )
    
    auditor_skill = A2AAgentSkill(
        id="auditor_agent",
        name="Sustainability Auditor",
        description="Evaluates code plans for eco-friendliness",
        tags=["sustainability", "audit"]
    )
    
    full_stack_skill = A2AAgentSkill(
        id="full_stack_agent",
        name="Full Stack Sustainable Agent",
        description="Orchestrates planning, execution, and auditing of sustainable code generation",
        tags=["react", "sustainability", "code-generation"]
    )
    
    # Create A2A servers with MCP support for each agent
    planner_server = create_a2a_server_with_mcp(
        planner_agent,
        planner_skill,
        "http://host.docker.internal:9001/",
        supports_json_input=False
    )
    
    executor_server = create_a2a_server_with_mcp(
        executor_agent,
        executor_skill,
        "http://host.docker.internal:9002/",
        supports_json_input=True
    )
    
    auditor_server = create_a2a_server_with_mcp(
        auditor_agent,
        auditor_skill,
        "http://host.docker.internal:9003/",
        supports_json_input=True
    )
    
    full_stack_server = create_a2a_server_with_mcp(
        full_stack_agent,
        full_stack_skill,
        "http://host.docker.internal:9004/",
        supports_json_input=False
    )
    
    # Log the server starting
    print("Starting A2A servers with MCP support for all agents...")
    print(f"Planner Agent: http://host.docker.internal:9001 (MCP enabled)")
    print(f"Executor Agent: http://host.docker.internal:9002 (MCP enabled)")
    print(f"Auditor Agent: http://host.docker.internal:9003 (MCP enabled)")
    print(f"Full Stack Agent: http://host.docker.internal:9004 (MCP enabled)")
    print("-" * 50)
    
    # Run all servers concurrently
    await asyncio.gather(
        planner_server.start("0.0.0.0", 9001),
        executor_server.start("0.0.0.0", 9002),
        auditor_server.start("0.0.0.0", 9003),
        full_stack_server.start("0.0.0.0", 9004)
    )

if __name__ == "__main__":
    asyncio.run(main())
