CSV_DIR = "/data/data/com.termux/files/home/storage/documents/10k_synthea_covid19_csv/"
OUTPUT_PATH = "output/covid_mortality_demographics/data.json"

import pandas as pd
import json
import os

CSV_DIR = "/data/data/com.termux/files/home/storage/documents/10k_synthea_covid19_csv/"
OUTPUT_PATH = "output/covid_mortality_demographics/data.json"

try:
    # Read patients.csv
    patients_df = pd.read_csv(os.path.join(CSV_DIR, "patients.csv"))

    # Filter for deceased patients (DEATHDATE is not null)
    deceased_patients = patients_df[patients_df['DEATHDATE'].notna()].copy()

    # Select required columns
    extracted_data = deceased_patients[['Id', 'BIRTHDATE', 'DEATHDATE', 'RACE', 'GENDER']].to_dict('records')

    # Save to JSON
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(extracted_data, f, indent=4)

    print(f"Successfully extracted and saved data to {OUTPUT_PATH}")

except FileNotFoundError:
    print(f"Error: patients.csv not found in {CSV_DIR}")
except Exception as e:
    print(f"An error occurred during processing: {e}")