import json
import sys
import os
from utils import load_prompt, call_llm



def load_json(json_name):
    if not os.path.exists(json_name):
        return []
    with open(json_name, "r", encoding="utf-8") as f:
        return json.load(f)

def run(input_conversation):
    system = load_prompt("note_prompt.md")
    raw = call_llm(system, str(input_conversation))

    print(raw)


if __name__ == "__main__":
    input_document = sys.argv[1]

    my_load = load_json(input_document)
    run(my_load)

