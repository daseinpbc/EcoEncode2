import os
import json
import asyncio
from typing import Annotated

from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

# --- Agent JWT & WebSocket Configuration ---

AGENT_JWT_FULL_STACK = os.getenv("AGENT_JWT_FULL_STACK")
AGENT_JWT_PLANNER = os.getenv("AGENT_JWT_PLANNER") 
AGENT_JWT_EXECUTOR = os.getenv("AGENT_JWT_EXECUTOR")
AGENT_JWT_AUDITOR = os.getenv("AGENT_JWT_AUDITOR")

WEBSOCKET_URL = "wss://poc.genai.works/ws"

# --- Session Initialization ---
session_full_stack = GenAISession(jwt_token=AGENT_JWT_FULL_STACK, ws_url=WEBSOCKET_URL)
session_planner = GenAISession(jwt_token=AGENT_JWT_PLANNER, ws_url=WEBSOCKET_URL)
session_executor = GenAISession(jwt_token=AGENT_JWT_EXECUTOR, ws_url=WEBSOCKET_URL)
session_auditor = GenAISession(jwt_token=AGENT_JWT_AUDITOR, ws_url=WEBSOCKET_URL)



# --- Agent 1: Planner Agent ---
@session_planner.bind(
    name="planner_agent",
    description="Analyzes a user's request and creates a sustainable coding plan."
)
async def planner_agent(
    agent_context: GenAIContext,
    user_request: Annotated[str, "The user's plain-text request."]
) -> dict:
    """Creates a JSON plan based on sustainable coding heuristics."""
    # Return a sample plan - in a real implementation, this would use the session's built-in LLM
    system_prompt = """
        You are the Green-Stack Planner. Analyze the user's request and create a JSON plan.
        Your output MUST be a JSON object with "components" and "optimizations" keys.
            ### SUSTAINABLE HEURISTICS RULEBOOK ###
    **1. Data Transfer & Network Usage:**
    - NextGenFormats: If images are mentioned, use .webp/.avif.
    - LazyLoading: For below-the-fold content, use React.lazy().
    - ResponsiveImages: For primary images, use the srcset attribute
    - CodeSplitting: For large, non-critical UI sections (charts, modals), code-split.
    - PayloadReduction: If fetching API data, fetch only necessary fields.
    - AvoidPolling: For real-time data, use WebSockets/SSE.

    **2. Computation & JavaScript Execution:**
    - Memoization: For any lists or grids, wrap items in React.memo.
    - ConditionalRendering: Unmount non-visible components instead of hiding with CSS.
    - DebounceStateUpdates: For frequent events like resizing, debounce handlers.
    - PromoteFlatState: When managing complex state, prefer a flatter structure.

    **3. Rendering & Browser Painting:**
    - PreferCSSTransitions: For simple hover animations/fades, use CSS.
    - HardwareAcceleratedProperties: Animate 'transform' and 'opacity'.
    - UseCSSVariablesForThemes: For theming (e.g., dark mode), use CSS Variables.
    """
     
    return {
        "components": ["React Component", "CSS Styling"],
        "optimizations": ["LazyLoading", "Memoization", "ResponsiveImages"]
    }


# --- Agent 2: Executor Agent ---
@session_executor.bind(
    name="executor_agent",
    description="Generates React code based on a provided JSON plan."
)
async def executor_agent(
    agent_context: GenAIContext,
    plan: Annotated[dict, "The JSON execution plan from the Planner Agent."]
) -> str:
    """Generates a single, self-contained React component from a plan."""
    # Return sample React code - in a real implementation, this would use the session's built-in LLM
    components = plan.get("components", [])
    optimizations = plan.get("optimizations", [])
    return f"""
import React from 'react';

const GeneratedComponent = () => {{
  // Components: {', '.join(components)}
  // Optimizations: {', '.join(optimizations)}
  
  return (
    <div style={{{{padding: '20px'}}}}>
      <h1>Generated React Component</h1>
      <p>This component was generated based on the plan.</p>
    </div>
  );
}};

export default GeneratedComponent;
"""


# --- Agent 3: Auditor Agent ---
@session_auditor.bind(
    name="auditor_agent",
    description="Calculates an Eco-Grade based on a provided JSON plan."
)
async def auditor_agent(
    agent_context: GenAIContext,
    plan: Annotated[dict, "The JSON execution plan from the Planner Agent."]
) -> dict:
    """Calculates a sustainability score and generates a markdown report."""
    optimizations = plan.get("optimizations", [])
    components = plan.get("components", [])
    score = 100
    notes = []
    if "LazyLoading" in optimizations: score += 30; notes.append("✅ Implemented Lazy Loading (+30 pts)")
    if "Memoization" in optimizations: score += 20; notes.append("✅ Used Memoization (+20 pts)")
    is_list = any("List" in s or "Gallery" in s for s in components)
    if is_list and "Memoization" not in optimizations: score -= 15; notes.append("❌ Failed to memoize list items (-15 pts)")
    best_practices_score = min(max(score, 0), 100)
    page_weight_score = 85
    performance_score = 92
    eco_grade = (page_weight_score * 0.5) + (performance_score * 0.3) + (best_practices_score * 0.2)
    
    # Generate markdown report
    report_markdown = f"""
# Eco-Grade Report

**Overall Eco-Grade: {eco_grade:.1f}/100**

## Breakdown:
- Page Weight Score: {page_weight_score}/100
- Performance Score: {performance_score}/100  
- Best Practices Score: {best_practices_score}/100

## Notes:
{chr(10).join(notes) if notes else "No specific notes."}
"""
    
    return {"report_markdown": report_markdown, "eco_grade": eco_grade}


# --- Agent 4: The Orchestrator (Full Stack Agent) ---
@session_full_stack.bind(
    name="full_stack_agent",
    description="Orchestrates the planning, execution, and auditing of sustainable code generation."
)
async def full_stack_agent(
    agent_context: GenAIContext,
    prompt: Annotated[str, "The user's top-level request for code generation."]
) -> dict:
    """
    Accepts a prompt and returns a complete response with generated code and eco-grade.
    """
    print(f"--- Full Stack Agent received prompt: '{prompt}' ---")

    # Since GenAI agents run independently, we simulate the multi-agent workflow here
    # In a real implementation, this could coordinate with other agents via the GenAI platform
    
    # Simulate planner output
    plan = {
        "components": ["React Component", "CSS Styling"],
        "optimizations": ["LazyLoading", "Memoization", "ResponsiveImages"]
    }
    
    # Simulate executor output
    generated_code = """
import React from 'react';

const GeneratedComponent = () => {
  return (
    <div style={{padding: '20px'}}>
      <h1>Generated React Component</h1>
      <p>This component was generated for: {}</p>
    </div>
  );
};

export default GeneratedComponent;
""".format(prompt)
    
    # Simulate auditor output
    eco_grade = 95.5
    report_markdown = """
# Eco-Grade Report

**Overall Eco-Grade: 95.5/100**

## Breakdown:
- Page Weight Score: 85/100
- Performance Score: 92/100  
- Best Practices Score: 150/100

## Notes:
✅ Implemented Lazy Loading (+30 pts)
✅ Used Memoization (+20 pts)
"""

    return {
        "generatedCode": generated_code,
        "reportMarkdown": report_markdown,
        "ecoGrade": eco_grade
    }


# --- Application Startup ---
async def main():
    """Main function to start all agents and process their events concurrently."""
    print("Starting all agents...")
    await asyncio.gather(
        session_full_stack.process_events(),
        session_planner.process_events(),
        session_executor.process_events(),
        session_auditor.process_events()
    )

if __name__ == "__main__":
    asyncio.run(main())
