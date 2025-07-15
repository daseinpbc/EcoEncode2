# main_agentos.py

import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
# --- CORRECTED IMPORT ---
# We only need the 'Agent' base class.
from agentos import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize the Gemini LLM
# Make sure your GOOGLE_API_KEY is set in your environment (e.g., in the .env file)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")

# Initialize the FastAPI application
app = FastAPI()

# Define the data structure for incoming user requests
class UserRequest(BaseModel):
    
     prompt: str
# --- Agent Definitions ---

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

# --- Agent Instantiation ---
# We create instances of our agents to be used in the endpoint.
planner = PlannerAgent(llm)
executor = ExecutorAgent(llm)
auditor = AuditorAgent(llm)


# --- FastAPI Endpoint with Manual Orchestration ---
@app.post("/generate")
def run_orchestrator(request: UserRequest):
    """
    This endpoint manually orchestrates the agents by calling them in sequence.
    """
    # 1. Run the Planner to get the plan
    plan_result = planner.run(user_request=request.prompt)
    
    # 2. Run the Executor and Auditor with the plan
    generated_code = executor.run(plan=plan_result)
    report_result = auditor.run(plan=plan_result)
    
    # 3. Return the final, combined result
    return {
        "generatedCode": generated_code,
        "reportMarkdown": report_result["report_markdown"],
        "ecoGrade": report_result["eco_grade"] # Typo corrected here
    }
