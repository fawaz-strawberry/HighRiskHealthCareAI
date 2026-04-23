"""Manager Agent — takes a research question, produces a plan."""
import json
import sys
from utils import load_prompt, call_llm, save_artifact

def run(research_question):
    system = load_prompt("prompts/manager.md")
    raw = call_llm(system, research_question)

    # Try to parse JSON from response (strip junk if needed)
    start = raw.find("{")
    end = raw.rfind("}") + 1
    plan = json.loads(raw[start:end])

    task_id = plan["task_id"]
    save_artifact(task_id, "plan.json", json.dumps(plan, indent=2))
    print(f"[manager] Plan created — task_id: {task_id}")
    return plan

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else (
        "Analyze the demographics and outcomes of COVID-19 patients in the Synthea dataset. "
        "Focus on age distribution, gender breakdown, mortality rates, and most common conditions."
    )
    run(question)
