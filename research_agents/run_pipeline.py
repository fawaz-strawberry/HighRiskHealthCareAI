"""
Run the full research agent pipeline.

Usage:
    python run_pipeline.py <csv_dir> [research_question]

Example:
    python run_pipeline.py ./synthea_data "Analyze COVID-19 mortality by demographics"
"""
import sys
import json
from manager_agent import run as manager_run
from collector_agent import run as collector_run
from charter_agent import run as charter_run
from reporter_agent import run as reporter_run

def main():
    csv_dir = sys.argv[1] if len(sys.argv) > 1 else "./data"
    question = sys.argv[2] if len(sys.argv) > 2 else (
        "Analyze the demographics and outcomes of COVID-19 patients in the Synthea dataset. "
        "Focus on age distribution, gender breakdown, mortality rates, and most common conditions."
    )

    print("=" * 60)
    print("[pipeline] Starting research agent pipeline")
    print(f"[pipeline] Question: {question}")
    print(f"[pipeline] CSV dir:  {csv_dir}")
    print("=" * 60)

    # Step 1: Manager creates plan
    print("\n--- STEP 1: Manager Agent ---")
    plan = manager_run(question)
    task_id = plan["task_id"]

    # Step 2: Collector extracts data
    print("\n--- STEP 2: Collector Agent ---")
    if not collector_run(task_id, csv_dir, plan["collect_instructions"]):
        print("[pipeline] Collector failed. Check output/{task_id}/collect.py")
        return

    # Step 3: Charter creates visualizations
    print("\n--- STEP 3: Charter Agent ---")
    if not charter_run(task_id, plan["chart_instructions"]):
        print("[pipeline] Charter failed. Check output/{task_id}/charts.py")
        return

    # Step 4: Reporter generates LaTeX
    print("\n--- STEP 4: Reporter Agent ---")
    reporter_run(task_id, plan["report_instructions"])

    print("\n" + "=" * 60)
    print(f"[pipeline] DONE! All artifacts in: output/{task_id}/")
    print(f"  - plan.json      (manager's plan)")
    print(f"  - collect.py     (data extraction script)")
    print(f"  - data.json      (extracted data)")
    print(f"  - charts.py      (visualization script)")
    print(f"  - chart_*.png    (generated charts)")
    print(f"  - report.tex     (LaTeX report fragment)")
    print("=" * 60)

if __name__ == "__main__":
    main()
