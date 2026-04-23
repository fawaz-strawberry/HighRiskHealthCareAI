"""Collector Agent — generates and runs a data extraction script."""
import sys
import json
import subprocess
from utils import load_prompt, call_llm, save_artifact, load_artifact

def run(task_id, csv_dir, collect_instructions):
    system = load_prompt("prompts/collector.md")
    user_msg = (
        f"Instructions:\n{collect_instructions}\n\n"
        f"CSV_DIR will be: \"{csv_dir}\"\n"
        f"OUTPUT_PATH will be: \"output/{task_id}/data.json\""
    )
    code = call_llm(system, user_msg)

    # Strip markdown fences if model added them anyway
    code = code.replace("```python", "").replace("```", "").strip()

    # Inject variables at the top
    header = f'CSV_DIR = "{csv_dir}"\nOUTPUT_PATH = "output/{task_id}/data.json"\n\n'
    full_script = header + code

    script_path = save_artifact(task_id, "collect.py", full_script)

    print(f"[collector] Running extraction script...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[collector] ERROR:\n{result.stderr}")
        return False
    print(f"[collector] Data saved to output/{task_id}/data.json")
    return True

if __name__ == "__main__":
    task_id = sys.argv[1]
    csv_dir = sys.argv[2]
    plan = json.loads(load_artifact(task_id, "plan.json"))
    run(task_id, csv_dir, plan["collect_instructions"])
