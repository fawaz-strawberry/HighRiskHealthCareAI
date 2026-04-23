#!/usr/bin/env python3
"""
generate_food_report.py

Load the growing JSON food log, send it to a local Ollama model (default: gemma4:e2b),
and generate a markdown report.

Usage:
    python generate_food_report.py food_log.json
    python generate_food_report.py food_log.json --report reports/weekly_report.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests


DEFAULT_MODEL = "gemma4:e2b"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_REPORT_PATH = "food_report.md"

# -----------------------------
# Fully modifiable prompt text
# -----------------------------
SYSTEM_PROMPT = """You are a nutrition reporting assistant.

You will receive a JSON array containing structured food analysis records.
Your job is to write a clear markdown report summarizing the dataset.

Report requirements:
1. Use markdown headings and bullet points.
2. Summarize recurring food patterns, approximate macro trends, and notable health considerations.
3. Mention uncertainty where the upstream vision estimates may be unreliable.
4. Include practical observations, but do not present the report as medical advice.
5. Prefer concise tables only if they improve clarity.
6. Produce only markdown.
"""

USER_PROMPT_TEMPLATE = """Using the JSON food log below, generate a markdown report with these sections:

1. Executive Summary
2. Foods Logged
3. Macro Trends
4. Health Considerations
5. Repeated Patterns / Observations
6. Data Quality / Uncertainty Notes
7. Suggested Next Analysis Steps

JSON FOOD LOG:
{json_blob}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a markdown report from a JSON food log using local Ollama.")
    parser.add_argument("json_db", type=Path, help="Path to the growing JSON database.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL, help=f"Ollama generate endpoint (default: {DEFAULT_OLLAMA_URL})")
    parser.add_argument("--report", type=Path, default=Path(DEFAULT_REPORT_PATH), help=f"Markdown report path (default: {DEFAULT_REPORT_PATH})")
    parser.add_argument("--timeout", type=int, default=300, help="Request timeout in seconds.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature.")
    parser.add_argument("--num-predict", type=int, default=2000, help="Max tokens to generate.")
    return parser.parse_args()


def load_json_db(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"JSON DB not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON DB must be a top-level list.")
    return data


def call_ollama(
    *,
    url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout: int,
    temperature: float,
    num_predict: int,
) -> str:
    payload = {
        "model": model,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }

    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    raw = response.json()

    if "response" not in raw:
        raise RuntimeError(f"Unexpected Ollama response: {raw}")

    return raw["response"].strip()


def write_report(report_path: Path, markdown: str, *, model: str, source_db: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()

    full_md = f"""# Food Report

- **Generated at (UTC):** {generated_at}
- **Source DB:** `{source_db.resolve()}`
- **Model:** `{model}`

{markdown}
"""
    report_path.write_text(full_md, encoding="utf-8")


def main() -> int:
    args = parse_args()

    try:
        data = load_json_db(args.json_db)
    except Exception as exc:
        print(f"Could not load JSON DB: {exc}", file=sys.stderr)
        return 1

    json_blob = json.dumps(data, indent=2, ensure_ascii=False)
    user_prompt = USER_PROMPT_TEMPLATE.format(json_blob=json_blob)

    try:
        markdown = call_ollama(
            url=args.url,
            model=args.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            timeout=args.timeout,
            temperature=args.temperature,
            num_predict=args.num_predict,
        )
    except requests.RequestException as exc:
        print(f"Ollama request failed: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Report generation failed: {exc}", file=sys.stderr)
        return 3

    write_report(args.report, markdown, model=args.model, source_db=args.json_db)

    print("Saved report successfully.")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
