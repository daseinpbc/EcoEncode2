# main_agentos.py

import os
import json
import asyncio
from typing import Annotated

# GenAI Session and LangChain Imports
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from langchain_google_genai import ChatGoogleGenerativeAI

# Your existing Agent classes (no changes needed)
from agentos import Agent

# --- Agent JWT Configuration ---
# Replace with your actual agent JWT
AGENT_JWT = "your_agent_jwt_here" # TODO: Add your agent JWT here
session = GenAISession(jwt_token=AGENT_JWT)

# --- LLM and Agent Initialization ---
# Initialize the Gemini LLM that will be used by the agents
# It reads the GOOGLE_API_KEY from your environment
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")

# --- Agent Definitions (Copied from your previous code) ---

class PlannerAgent(Agent):
    """AGENT 1: The Planner."""
    def __init__(self, llm_instance):
        super().__init__()
        self.name = "PlannerAgent"
        self.system_prompt = """
You are the Green-Stack Planner. Analyze the user's request and create a JSON plan.
Your output MUST be a JSON object with "components" and "optimizations" keys.
### SUSTAINABLE HEURISTICS RULEBOOK ###
- NextGenFormats: If images are mentioned, use .webp/.avif.
- LazyLoading: For below-the-fold content, use React.lazy().
- ResponsiveImages: For primary images, use the srcset attribute.
- CodeSplitting: For large, non-critical UI sections (charts, modals), code-split.
- Memoization: For any lists or grids, wrap items in React.memo.
- UseCSSVariablesForThemes: For theming (e.g., dark mode), use CSS Variables.
### END RULEBOOK ###
USER REQUEST: "{user_request}"
YOUR JSON PLAN:
"""
        self.llm = llm_instance

    def run(self, user_request: str) -> dict:
        prompt = self.system_prompt.format(user_request=user_request)
        response = self.llm.invoke(prompt)
        cleaned_response = response.content.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)

class ExecutorAgent(Agent):
    """AGENT 2: The Executor."""
    def __init__(self, llm_instance):
        super().__init__()
        self.name = "ExecutorAgent"
        self.system_prompt = """
You are an expert React developer. Generate a single, self-contained React component that executes the following plan. The code should be functional and include styling.
EXECUTION PLAN:
{plan}
REACT CODE (HTML/JSX with inline CSS in a style tag):
"""
        self.llm = llm_instance
        
    def run(self, plan: dict) -> str:
        prompt = self.system_prompt.format(plan=json.dumps(plan, indent=2))
        response = self.llm.invoke(prompt)
        return response.content

class AuditorAgent(Agent):
    """AGENT 3: The Auditor."""
    def __init__(self, llm_instance):
        super().__init__()
        self.name = "AuditorAgent"
        self.report_prompt_template = "Format this data into a user-friendly markdown report: Eco-Grade: {grade}, Notes: {notes}"
        self.llm = llm_instance

    def run(self, plan: dict) -> dict:
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
        report_prompt = self.report_prompt_template.format(grade=eco_grade, notes=", ".join(notes))
        report_markdown = self.llm.invoke(report_prompt).content
        return {"report_markdown": report_markdown, "eco_grade": eco_grade}

# --- Main Agent Entry Point ---

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
    # 1. Instantiate the agents required for the workflow
    planner = PlannerAgent(llm)
    executor = ExecutorAgent(llm)
    auditor = AuditorAgent(llm)

    # 2. Run the orchestration logic
    # Note: The .run() methods are synchronous, but GenAISession handles the async event loop.
    plan_result = planner.run(user_request=prompt)
    generated_code = executor.run(plan=plan_result)
    report_result = auditor.run(plan=plan_result)

    # 3. Return the final, combined result
    return {
        "generatedCode": generated_code,
        "reportMarkdown": report_result["report_markdown"],
        "ecoGrade": report_result["eco_grade"]
    }

# --- Application Startup ---

async def main():
    print(f"Agent 'full_stack_agent' started. Waiting for events...")
    await session.process_events()

if __name__ == "__main__":
    # This will run the agent and connect to the GenAI OS infrastructure.
    # Ensure your GOOGLE_API_KEY is set as an environment variable.
    asyncio.run(main())
