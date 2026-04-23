DATA_PATH = "output/covid_mortality_demographics/data.json"
CHART_DIR = "output/covid_mortality_demographics"

import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

DATA_PATH = "output/covid_mortality_demographics/data.json"
CHART_DIR = "output/covid_mortality_demographics"

try:
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: Data file not found at {DATA_PATH}")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {DATA_PATH}")
    exit()

# Ensure the output directory exists
os.makedirs(CHART_DIR, exist_ok=True)

# --- Data Processing ---
ages = []
race_gender_data = {}

for record in data:
    try:
        birth_date = datetime.strptime(record['BIRTHDATE'], '%Y-%m-%d')
        death_date_str = record['DEATHDATE']
        
        if death_date_str is not None:
            death_date = datetime.strptime(death_date_str, '%Y-%m-%d')
            age = (death_date - birth_date).days
            ages.append(age)
            
            race = record['RACE']
            gender = record['GENDER']
            
            key = (race, gender)
            if key not in race_gender_data:
                race_gender_data[key] = []
            race_gender_data[key].append(1) # Count the death event
            
    except (ValueError, TypeError) as e:
        # Skip records with invalid dates or missing required fields
        # print(f"Skipping record due to error: {e}")
        continue

# --- Chart 1: Histogram of Mortality by Age Groups ---
if ages:
    plt.figure(figsize=(10, 6))
    
    # Determine appropriate age bins
    min_age = min(ages)
    max_age = max(ages)
    
    # Create bins based on age distribution
    bins = range(int(min_age) - 1, int(max_age) + 2)
    
    plt.hist(ages, bins=bins, edgecolor='black', rwidth=0.8)
    
    plt.title('Distribution of Mortality by Age Groups')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    
    chart_path_1 = os.path.join(CHART_DIR, 'chart_1.png')
    plt.tight_layout()
    plt.savefig(chart_path_1)
    print(f"Chart saved to: {chart_path_1}")
else:
    print("No valid mortality data found to create the histogram.")


# --- Chart 2: Grouped Bar Charts (Mortality Rate by Race and Gender) ---
if race_gender_data:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Mortality Distribution Segmented by Race and Gender', fontsize=16)

    # Plot 1: Mortality by Race
    race_counts = {}
    for (race, gender), counts in race_gender_data.items():
        if race not in race_counts:
            race_counts[race] = []
        race_counts[race].extend(counts)
    
    race_labels = list(race_counts.keys())
    race_data = [race_counts[r] for r in race_labels]

    axes[0].bar(race_labels, race_data, color=['skyblue', 'lightcoral', 'lightgreen', 'gold'])
    axes[0].set_title('Mortality Count by Race')
    axes[0].set_xlabel('Race')
    axes[0].set_ylabel('Number of Mortality Events')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].tight_layout()
    
    # Plot 2: Mortality by Gender
    gender_counts = {}
    for (race, gender), counts in race_gender_data.items():
        if gender not in gender_counts:
            gender_counts[gender] = []
        gender_counts[gender].extend(counts)

    gender_labels = list(gender_counts.keys())
    gender_data = [gender_counts[g] for g in gender_labels]

    axes[1].bar(gender_labels, gender_data, color=['salmon', 'lightskyblue', 'lightgreen', 'gold'])
    axes[1].set_title('Mortality Count by Gender')
    axes[1].set_xlabel('Gender')
    axes[1].set_ylabel('Number of Mortality Events')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].tight_layout()

    chart_path_2 = os.path.join(CHART_DIR, 'chart_2.png')
    plt.savefig(chart_path_2)
    print(f"Chart saved to: {chart_path_2}")

print("\nProcess complete.")