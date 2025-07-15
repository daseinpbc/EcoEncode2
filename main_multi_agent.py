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
     # 1. Calculate Best Practices Score
    best_practices_score = 70  # Base score
    notes = []
    
    # --- Data Transfer & Network Usage Heuristics ---
    if "NextGenFormats" in optimizations: 
        best_practices_score += 10
        notes.append("✅ Using next-gen image formats (.webp/.avif) (+10 pts)")
    else:
        best_practices_score -= 5
        notes.append("❌ Not using next-gen image formats (-5 pts)")
    
    if "LazyLoading" in optimizations: 
        best_practices_score += 15
        notes.append("✅ Implemented lazy loading for below-the-fold content (+15 pts)")
    else:
        has_large_content = any("Table" in s or "List" in s or "Gallery" in s for s in components)
        if has_large_content:
            best_practices_score -= 10
            notes.append("❌ Missing lazy loading for large content (-10 pts)")
    
    if "ResponsiveImages" in optimizations: 
        best_practices_score += 10
        notes.append("✅ Using responsive images with srcset attribute (+10 pts)")
    else:
        has_images = any("Image" in s or "Photo" in s or "Banner" in s for s in components)
        if has_images:
            best_practices_score -= 5
            notes.append("❌ Not using responsive images (-5 pts)")
    
    if "CodeSplitting" in optimizations: 
        best_practices_score += 10
        notes.append("✅ Implemented code splitting for large UI sections (+10 pts)")
    else:
        has_complex_ui = any("Chart" in s or "Dashboard" in s or "Modal" in s for s in components)
        if has_complex_ui:
            best_practices_score -= 5
            notes.append("❌ Missing code splitting for complex UI elements (-5 pts)")
    
    if "PayloadReduction" in optimizations: 
        best_practices_score += 8
        notes.append("✅ Optimized API data fetching to reduce payload size (+8 pts)")
    else:
        has_data_fetching = any("Table" in s or "List" in s or "Data" in s for s in components)
        if has_data_fetching:
            best_practices_score -= 5
            notes.append("❌ Not optimizing API data payload size (-5 pts)")
    
    if "AvoidPolling" in optimizations: 
        best_practices_score += 8
        notes.append("✅ Using WebSockets/SSE instead of polling (+8 pts)")
    else:
        has_realtime = any("Realtime" in s or "Live" in s or "Feed" in s for s in components)
        if has_realtime:
            best_practices_score -= 8
            notes.append("❌ Using polling instead of WebSockets/SSE (-8 pts)")
    
    # --- Computation & JavaScript Execution Heuristics ---
    if "Memoization" in optimizations: 
        best_practices_score += 12
        notes.append("✅ Using memoization for list/grid items (+12 pts)")
    else:
        is_list = any("List" in s or "Table" in s or "Grid" in s for s in components)
        if is_list:
            best_practices_score -= 10
            notes.append("❌ Missing memoization for list/grid items (-10 pts)")
    
    if "ConditionalRendering" in optimizations: 
        best_practices_score += 8
        notes.append("✅ Properly unmounting non-visible components (+8 pts)")
    else:
        has_conditional_ui = any("Tab" in s or "Modal" in s or "Accordion" in s for s in components)
        if has_conditional_ui:
            best_practices_score -= 5
            notes.append("❌ Using CSS to hide components instead of unmounting (-5 pts)")
    
    if "DebounceStateUpdates" in optimizations: 
        best_practices_score += 8
        notes.append("✅ Debouncing frequent event handlers (+8 pts)")
    else:
        has_frequent_events = any("Search" in s or "Filter" in s or "Resize" in s for s in components)
        if has_frequent_events:
            best_practices_score -= 5
            notes.append("❌ Not debouncing frequent events (-5 pts)")
    
    if "PromoteFlatState" in optimizations: 
        best_practices_score += 8
        notes.append("✅ Using flat state structure for better performance (+8 pts)")
    else:
        has_complex_state = any("Form" in s or "Filter" in s or "Dashboard" in s for s in components)
        if has_complex_state:
            best_practices_score -= 5
            notes.append("❌ Using deeply nested state structure (-5 pts)")
    
    # --- Rendering & Browser Painting Heuristics ---
    if "PreferCSSTransitions" in optimizations: 
        best_practices_score += 8
        notes.append("✅ Using CSS for simple animations instead of JS (+8 pts)")
    else:
        has_animations = any("Animation" in s or "Transition" in s or "Hover" in s for s in components)
        if has_animations:
            best_practices_score -= 5
            notes.append("❌ Using JS for animations that could be CSS (-5 pts)")
    
    if "HardwareAcceleratedProperties" in optimizations: 
        best_practices_score += 8
        notes.append("✅ Using hardware-accelerated properties for animations (+8 pts)")
    else:
        has_animations = any("Animation" in s or "Transition" in s for s in components)
        if has_animations:
            best_practices_score -= 5
            notes.append("❌ Not using hardware-accelerated properties (-5 pts)")
    
    if "UseCSSVariablesForThemes" in optimizations: 
        best_practices_score += 8
        notes.append("✅ Using CSS variables for theming (+8 pts)")
    else:
        has_theming = any("Theme" in s or "Dark" in s or "Style" in s for s in components)
        if has_theming:
            best_practices_score -= 5
            notes.append("❌ Not using CSS variables for theming (-5 pts)")
    
    # Cap score between 0 and 100
    best_practices_score = min(max(best_practices_score, 0), 100)
    
    # 2. Calculate Page Weight Score (MOCKED VALUES)
    mock_total_page_weight_kb = 750 
    page_weight_score = 85

    # 3. Calculate Performance Score (MOCKED VALUES)
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

## Sustainability Analysis:
{chr(10).join(notes) if notes else "No specific notes."}

## Recommendations:
"""
    
    # Add recommendations based on missing optimizations
    missing_optimizations = []
    all_optimizations = [
        "NextGenFormats", "LazyLoading", "ResponsiveImages", "CodeSplitting", 
        "PayloadReduction", "AvoidPolling", "Memoization", "ConditionalRendering", 
        "DebounceStateUpdates", "PromoteFlatState", "PreferCSSTransitions", 
        "HardwareAcceleratedProperties", "UseCSSVariablesForThemes"
    ]
    
    for opt in all_optimizations:
        if opt not in optimizations:
            if opt == "NextGenFormats":
                missing_optimizations.append("- Use WebP or AVIF image formats instead of PNG/JPEG to reduce file sizes")
            elif opt == "LazyLoading":
                missing_optimizations.append("- Implement React.lazy() for components that aren't immediately visible")
            elif opt == "ResponsiveImages":
                missing_optimizations.append("- Use the srcset attribute to serve different image sizes based on viewport")
            elif opt == "CodeSplitting":
                missing_optimizations.append("- Implement code-splitting for large components to reduce initial load time")
            elif opt == "PayloadReduction":
                missing_optimizations.append("- Only fetch necessary fields from your API to reduce data transfer")
            elif opt == "AvoidPolling":
                missing_optimizations.append("- Replace polling with WebSockets or Server-Sent Events for real-time updates")
            elif opt == "Memoization":
                missing_optimizations.append("- Use React.memo() for list items to prevent unnecessary re-renders")
            elif opt == "ConditionalRendering":
                missing_optimizations.append("- Unmount non-visible components instead of hiding them with CSS")
            elif opt == "DebounceStateUpdates":
                missing_optimizations.append("- Implement debouncing for event handlers that trigger frequent updates")
            elif opt == "PromoteFlatState":
                missing_optimizations.append("- Flatten your state structure to improve performance")
            elif opt == "PreferCSSTransitions":
                missing_optimizations.append("- Use CSS transitions instead of JavaScript for simple animations")
            elif opt == "HardwareAcceleratedProperties":
                missing_optimizations.append("- Animate transform and opacity properties for better performance")
            elif opt == "UseCSSVariablesForThemes":
                missing_optimizations.append("- Implement CSS variables for theming to reduce JavaScript overhead")
    
    # Add recommendations to the report
    if missing_optimizations:
        report_text += "\n" + "\n".join(missing_optimizations)
    else:
        report_text += "\nNo specific recommendations. All sustainable practices are already implemented."
    
    return {
        "report_markdown": report_text, 
        "eco_grade": eco_grade,
        "best_practices_score": best_practices_score,
        "page_weight_score": page_weight_score,
        "performance_score": performance_score,
        "notes": notes,
        "recommendations": missing_optimizations
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
