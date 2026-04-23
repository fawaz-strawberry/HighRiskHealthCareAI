CSV_DIR = "/data/data/com.termux/files/home/storage/documents/10k_synthea_covid19_csv/"
OUTPUT_PATH = "output/covid_mortality_demographics/data.json"

import pandas as pd
import json
import os

CSV_DIR = "/data/data/com.termux/files/home/storage/documents/10k_synthea_covid19_csv/"
OUTPUT_PATH = "output/covid_mortality_demographics/data.json"
FILE_NAME = "patients.csv"

try:
    # Construct the full path to the input file
    input_file_path = os.path.join(CSV_DIR, FILE_NAME)

    # 1. Read the CSV file
    df = pd.read_csv(input_file_path)

    # 2. Filter and select the required columns
    required_columns = ["BIRTHDATE", "DEATHDATE", "RACE", "GENDER"]
    
    # Ensure all required columns exist before selecting (robustness check)
    existing_columns = [col for col in required_columns if col in df.columns]
    
    if not existing_columns:
        print(f"Error: One or more required columns ({required_columns}) not found in {FILE_NAME}.")
    else:
        result_df = df[existing_columns]

        # Convert DataFrame to a list of records (JSON friendly)
        data_list = result_df.to_dict(orient='records')

        # 3. Save the result as a single JSON file
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(data_list, f, separators=(',', ':'))

        print(f"Successfully extracted data from {FILE_NAME} and saved to {OUTPUT_PATH}")

except FileNotFoundError:
    print(f"Error: The file {input_file_path} was not found. Please check CSV_DIR and FILE_NAME.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")