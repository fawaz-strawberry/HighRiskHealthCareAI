import os
import sys
import json
import csv

def main():
    csv_dir = sys.argv[1] if len(sys.argv) > 1 else "./data"
    headers = {}

    for fname in sorted(os.listdir(csv_dir)):
        if not fname.lower().endswith(".csv"):
            continue
        filepath = os.path.join(csv_dir, fname)
        with open(filepath, "r", newline="") as f:
            reader = csv.reader(f)
            row = next(reader, None)
            if row:
                headers[fname] = row

    out_path = os.path.join(csv_dir, "csv_headers.json")
    with open(out_path, "w") as f:
        json.dump(headers, f, indent=2)

    # Also print it nicely so you can copy-paste
    print(json.dumps(headers, indent=2))
    print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    main()
