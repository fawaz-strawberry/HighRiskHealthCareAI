"""Charter Agent — generates and runs a chart-creation script."""
import sys
import json
import subprocess
from utils import load_prompt, call_llm, save_artifact, load_artifact

def run(task_id, chart_instructions):
    system = load_prompt("prompts/charter.md")
    data_sample = json.loads(load_artifact(task_id, "data.json"))[0]
    user_msg = (
        f"Instructions:\n{chart_instructions}\n\n"
        f"DATA_PATH will be: \"output/{task_id}/data.json\"\n"
        f"The data is in a json list that looks like the following format: \n {data_sample} \n"\
        f"CHART_DIR will be: \"output/{task_id}\""
    )
    code = call_llm(system, user_msg)
    code = code.replace("```python", "").replace("```", "").strip()

    header = (
        f'DATA_PATH = "output/{task_id}/data.json"\n'
        f'CHART_DIR = "output/{task_id}"\n\n'
    )
    full_script = header + code

    script_path = save_artifact(task_id, "charts.py", full_script)

    print(f"[charter] Running chart script...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[charter] ERROR:\n{result.stderr}")
        return False
    print(f"[charter] Charts saved to output/{task_id}/")
    return True

if __name__ == "__main__":
    task_id = sys.argv[1]
    plan = json.loads(load_artifact(task_id, "plan.json"))
    run(task_id, plan["chart_instructions"])
