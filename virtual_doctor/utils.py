import requests
import json
import os

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:e2b"

def load_prompt(prompt_path):
    with open(prompt_path, "r") as f:
        return f.read().strip()

def call_llm(system_prompt, user_message, temperature=0.3):
    """Single call to Ollama. Returns the assistant's text response."""
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "options": {"temperature": temperature},
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["message"]["content"]

def ensure_task_dir(task_id):
    path = os.path.join("output", task_id)
    os.makedirs(path, exist_ok=True)
    return path

def save_artifact(task_id, filename, content):
    task_dir = ensure_task_dir(task_id)
    filepath = os.path.join(task_dir, filename)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"  [saved] {filepath}")
    return filepath

def load_artifact(task_id, filename):
    filepath = os.path.join("output", task_id, filename)
    with open(filepath, "r") as f:
        return f.read()
