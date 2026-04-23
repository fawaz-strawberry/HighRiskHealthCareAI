# Gemma 4 food pipeline

Files:
- `analyze_food_image.py`: send a food image to local Ollama `gemma4:e2b`, save markdown, append structured record to JSON.
- `generate_food_report.py`: load the growing JSON file, ask the same model for a full markdown report.

Basic usage:
```bash
pip install -r requirements.txt
ollama pull gemma4:e2b

python analyze_food_image.py ./example_food.jpg
python generate_food_report.py ./food_log.json --report ./reports/food_report.md
```

Notes:
- Ollama listens on `http://localhost:11434` by default.
- The first script uses structured output with a JSON schema to keep fields consistent.
- The second script sends the full JSON database into the model prompt, which is fine while the log is moderate in size. For very large logs, chunking or pre-aggregation will be better.
