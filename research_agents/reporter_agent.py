"""Reporter Agent — generates LaTeX report fragment."""
import sys
import os
import json
from utils import load_prompt, call_llm, save_artifact, load_artifact

def run(task_id, report_instructions):
    system = load_prompt("prompts/reporter.md")

    # Find chart files
    task_dir = os.path.join("output", task_id)
    charts = sorted([f for f in os.listdir(task_dir) if f.endswith(".png")])

    # Load data summary (first 2000 chars to keep context small)
    data_raw = load_artifact(task_id, "data.json")
    data_preview = data_raw[:2000]

    user_msg = (
        f"Instructions:\n{report_instructions}\n\n"
        f"Chart filenames: {charts}\n\n"
        f"Data (may be truncated):\n{data_preview}"
    )
    latex = call_llm(system, user_msg)
    latex = latex.replace("```latex", "").replace("```", "").strip()

    save_artifact(task_id, "report.tex", latex)
    print(f"[reporter] Report saved to output/{task_id}/report.tex")
    return True

if __name__ == "__main__":
    task_id = sys.argv[1]
    plan = json.loads(load_artifact(task_id, "plan.json"))
    run(task_id, plan["report_instructions"])
