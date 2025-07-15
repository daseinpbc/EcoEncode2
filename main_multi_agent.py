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

# Use host.docker.internal to connect to local router from Docker container
WEBSOCKET_URL = "ws://host.docker.internal:8080/ws"

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
      # 1. Calculate Best Practices Score
    best_practices_score = 100
    notes = []
    # Bonuses
    if "LazyLoading" in optimizations: best_practices_score += 30; notes.append("✅ Implemented Lazy Loading (+30 pts)")
    if "Memoization" in optimizations: best_practices_score += 20; notes.append("✅ Used Memoization for list items (+20 pts)")
    if "ResponsiveImages" in optimizations: best_practices_score += 20; notes.append("✅ Planned for Responsive Images (+20 pts)")
    if "UseCSSVariablesForThemes" in optimizations: best_practices_score += 15; notes.append("✅ Used CSS Variables for Theming (+15 pts)")
    if "PreferCSSTransitions" in optimizations: best_practices_score += 15; notes.append("✅ Preferred CSS Transitions (+15 pts)")
    # Penalties
    is_list = any("List" in s or "Gallery" in s for s in plan.get("components", []))
    if is_list and "Memoization" not in optimizations: best_practices_score -= 15; notes.append("❌ Failed to memoize list items (-15 pts)")
    if "NextGenFormats" not in optimizations: best_practices_score -= 10; notes.append("❌ Did not use modern image formats (-10 pts)")
    # Cap score at 100 for display
    best_practices_score = min(max(best_practices_score, 0), 100)
    
    # 2. Calculate Page Weight Score (MOCKED VALUES)
    # In a real app, you would get these numbers from a build process or performance audit tool.
    mock_total_page_weight_kb = 750 
   
    #if mock_total_page_weight_kb < 500: page_weight_score = 100
    #elif mock_total_page_weight_kb <= 1000: page_weight_score = 85
    #elif mock_total_page_weight_kb <= 2000: page_weight_score = 60
    #elif mock_total_page_weight_kb <= 4000: page_weight_score = 30
    #else: page_weight_score = 10
    page_weight_score = 85

    # 3. Calculate Performance Score (MOCKED VALUES)
    # In a real app, you would get these from a tool like Google's PageSpeed Insights API.
    mock_lcp_s = 2.8
    mock_inp_ms = 150
    lcp_score = 100 if mock_lcp_s < 2.5 else 50 if mock_lcp_s <= 4.0 else 0
    inp_score = 100 if mock_inp_ms < 200 else 50 if mock_inp_ms <= 500 else 0
    performance_score = (lcp_score * 0.6) + (inp_score * 0.4)

    # 4. Final Eco-Grade Calculation
    eco_grade = (page_weight_score * 0.5) + (performance_score * 0.3) + (best_practices_score * 0.2)

    # 5. Generate Report Text
    report_text = f"""
### 🌍 Eco-Grade Report

Your code achieved an Eco-Grade of **{eco_grade:.0f}/100**.

---

#### Score Breakdown:
* **Page Weight Score:** {page_weight_score}/100 `(mocked)`
* **Performance Score:** {performance_score:.0f}/100 `(mocked)`
* **Best Practices Score:** {best_practices_score}/100


## Notes:
{chr(10).join(notes) if notes else "No specific notes."}
"""
    
    return {"report_markdown": report_text, "eco_grade": eco_grade}


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
