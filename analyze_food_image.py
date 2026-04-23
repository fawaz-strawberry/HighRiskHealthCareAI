#!/usr/bin/env python3
"""
analyze_food_image.py

Send a food image to a local Ollama model (default: gemma4:e2b),
request a consistent structured nutrition summary, save the result
to a markdown file, and append the structured record to a growing JSON file.

Usage:
    python analyze_food_image.py path/to/food.jpg
    python analyze_food_image.py path/to/food.jpg --db data/food_log.json --out-dir outputs

Notes:
- This script expects Ollama to be running locally on http://localhost:11434
- It uses structured output (JSON Schema) for more consistent parsing.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests


DEFAULT_MODEL = "gemma4:e2b"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_DB_PATH = "food_log.json"
DEFAULT_OUTPUT_DIR = "food_outputs"

# -----------------------------
# Fully modifiable prompt text
# -----------------------------
SYSTEM_PROMPT = """You are a food nutrition estimation assistant.

The user will provide a single image that is expected to contain food.
Your task is to identify the main food item or meal and estimate its macros.

Rules:
1. Return ONLY data matching the provided JSON schema.
2. Use a single consistent canonical name for the detected food item.
3. If the image shows multiple foods, identify the primary meal name and list major components separately.
4. Macros should be practical estimates, not medical facts.
5. Include concise health considerations such as allergens, sodium, saturated fat, added sugar, fiber, protein quality, and processing level when relevant.
6. If the image quality is poor or uncertain, say so in uncertainty_notes and lower confidence.
7. Never invent exact serving sizes unless clearly visible; use estimated serving descriptions.
"""

USER_PROMPT_TEMPLATE = """Analyze this food image and produce a structured nutrition estimate.

Focus on:
- canonical food item naming
- estimated calories
- estimated protein, carbs, fat, fiber, sugar, sodium
- likely ingredients/components
- key health considerations
- uncertainty notes

Return the result strictly in the requested JSON schema.
"""

OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "food_item": {"type": "string"},
        "food_category": {"type": "string"},
        "serving_estimate": {"type": "string"},
        "ingredients_or_components": {
            "type": "array",
            "items": {"type": "string"}
        },
        "estimated_macros": {
            "type": "object",
            "properties": {
                "calories_kcal": {"type": "number"},
                "protein_g": {"type": "number"},
                "carbs_g": {"type": "number"},
                "fat_g": {"type": "number"},
                "fiber_g": {"type": "number"},
                "sugar_g": {"type": "number"},
                "sodium_mg": {"type": "number"}
            },
            "required": [
                "calories_kcal",
                "protein_g",
                "carbs_g",
                "fat_g",
                "fiber_g",
                "sugar_g",
                "sodium_mg"
            ],
            "additionalProperties": False
        },
        "health_considerations": {
            "type": "array",
            "items": {"type": "string"}
        },
        "uncertainty_notes": {"type": "string"},
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        }
    },
    "required": [
        "food_item",
        "food_category",
        "serving_estimate",
        "ingredients_or_components",
        "estimated_macros",
        "health_considerations",
        "uncertainty_notes",
        "confidence"
    ],
    "additionalProperties": False
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a food image with local Ollama.")
    parser.add_argument("image", type=Path, help="Path to the input food image.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL, help=f"Ollama generate endpoint (default: {DEFAULT_OLLAMA_URL})")
    parser.add_argument("--db", type=Path, default=Path(DEFAULT_DB_PATH), help=f"Path to growing JSON database (default: {DEFAULT_DB_PATH})")
    parser.add_argument("--out-dir", type=Path, default=Path(DEFAULT_OUTPUT_DIR), help=f"Directory for markdown outputs (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--timeout", type=int, default=180, help="Request timeout in seconds.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature.")
    parser.add_argument("--num-predict", type=int, default=800, help="Max tokens to generate.")
    return parser.parse_args()


def encode_image_to_base64(image_path: Path) -> str:
    with image_path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "food-item"


def ensure_json_db(db_path: Path) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []
    try:
        with db_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        raise ValueError("JSON database must be a top-level list.")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse JSON database at {db_path}: {exc}") from exc


def save_json_db(db_path: Path, data: List[Dict[str, Any]]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with db_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def call_ollama(
    *,
    url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    image_b64: str,
    timeout: int,
    temperature: float,
    num_predict: int,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "system": system_prompt,
        "prompt": user_prompt,
        "images": [image_b64],
        "format": OUTPUT_SCHEMA,
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

    text = raw["response"].strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model output was not valid JSON:\n{text}") from exc

    return parsed


def build_record(image_path: Path, model_output: Dict[str, Any]) -> Dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "id": f"{datetime.now().strftime('%Y%m%dT%H%M%S')}_{slugify(model_output['food_item'])}",
        "created_at_utc": timestamp,
        "source_image": str(image_path.resolve()),
        "model": DEFAULT_MODEL,
        "analysis": model_output,
    }
    return record


def write_markdown(record: Dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    food_item = record["analysis"]["food_item"]
    slug = slugify(food_item)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    md_path = out_dir / f"{stamp}_{slug}.md"

    macros = record["analysis"]["estimated_macros"]
    components = "\n".join(f"- {item}" for item in record["analysis"]["ingredients_or_components"])
    health = "\n".join(f"- {item}" for item in record["analysis"]["health_considerations"])

    md = f"""# Food Analysis

## Metadata
- **ID:** {record["id"]}
- **Created (UTC):** {record["created_at_utc"]}
- **Source image:** `{record["source_image"]}`
- **Model:** `{record["model"]}`

## Food Identification
- **Food item:** {record["analysis"]["food_item"]}
- **Category:** {record["analysis"]["food_category"]}
- **Serving estimate:** {record["analysis"]["serving_estimate"]}
- **Confidence:** {record["analysis"]["confidence"]}

## Components
{components if components else "- None detected"}

## Estimated Macros
- **Calories (kcal):** {macros["calories_kcal"]}
- **Protein (g):** {macros["protein_g"]}
- **Carbs (g):** {macros["carbs_g"]}
- **Fat (g):** {macros["fat_g"]}
- **Fiber (g):** {macros["fiber_g"]}
- **Sugar (g):** {macros["sugar_g"]}
- **Sodium (mg):** {macros["sodium_mg"]}

## Health Considerations
{health if health else "- None listed"}

## Uncertainty Notes
{record["analysis"]["uncertainty_notes"]}
"""

    md_path.write_text(md, encoding="utf-8")
    return md_path


def main() -> int:
    args = parse_args()

    if not args.image.exists():
        print(f"Image not found: {args.image}", file=sys.stderr)
        return 1

    image_b64 = encode_image_to_base64(args.image)

    try:
        model_output = call_ollama(
            url=args.url,
            model=args.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT_TEMPLATE,
            image_b64=image_b64,
            timeout=args.timeout,
            temperature=args.temperature,
            num_predict=args.num_predict,
        )
    except requests.RequestException as exc:
        print(f"Ollama request failed: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return 3

    record = build_record(args.image, model_output)
    record["model"] = args.model

    db = ensure_json_db(args.db)
    db.append(record)
    save_json_db(args.db, db)

    md_path = write_markdown(record, args.out_dir)

    print("Saved analysis successfully.")
    print(f"Markdown: {md_path}")
    print(f"JSON DB:  {args.db}")
    print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
