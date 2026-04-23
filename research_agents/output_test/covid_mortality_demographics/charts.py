DATA_PATH = "output/covid_mortality_demographics/data.json"
CHART_DIR = "output/covid_mortality_demographics"

import json
import os
import matplotlib.pyplot as plt
import numpy as np

DATA_PATH = "output/covid_mortality_demographics/data.json"
CHART_DIR = "output/covid_mortality_demographics"

# Ensure the directory exists
os.makedirs(CHART_DIR, exist_ok=True)

# Load the data
try:
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: Data file not found at {DATA_PATH}")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {DATA_PATH}")
    exit()

# --- Data Preparation ---

# Assuming the data structure contains fields like 'RACE', 'GENDER', 'AGE', 'COUNT_OF_DEATHS', 'BIRTHDATE', 'DEATHDATE'
# We need to calculate mortality rates and extract age information.

# For simplicity and robustness, we will aggregate the data based on the requested charts.

# 1. Mortality rate by Race (Bar Chart)
race_data = {}
for entry in data:
    race = entry.get('RACE')
    deaths = entry.get('COUNT_OF_DEATHS', 0)
    
    if race:
        if race not in race_data:
            race_data[race] = {'total_deaths': 0, 'total_population': 0}
        
        race_data[race]['total_deaths'] += deaths
        # Assuming we need a population denominator for a true rate, but based on instructions, we plot 'Count of Deaths'
        # If 'Mortality rate' is already present, we use that. Since the instruction asks for 'Count of Deaths' on the Y-axis, we use that.

# 2. Mortality rate by Gender and Race (Grouped Bar Chart)
gender_race_data = {}
for entry in data:
    race = entry.get('RACE')
    gender = entry.get('GENDER')
    mortality_rate = entry.get('MORTALITY_RATE') # Assuming this field exists for the grouped chart
    
    if race and gender and mortality_rate is not None:
        key = (race, gender)
        if key not in gender_race_data:
            gender_race_data[key] = []
        gender_race_data[key].append(mortality_rate)

# 3. Age distribution of deaths (Histogram)
age_counts = {}
for entry in data:
    age = entry.get('AGE')
    deaths = entry.get('COUNT_OF_DEATHS', 0)
    
    if age is not None:
        if age not in age_counts:
            age_counts[age] = 0
        age_counts[age] += deaths

# --- Chart Generation ---

# Chart 1: Mortality rate by Race (Bar Chart)
if race_data:
    race_labels = list(race_data.keys())
    race_counts = [race_data[r]['total_deaths'] for r in race_labels]
    
    plt.figure(figsize=(10, 6))
    plt.bar(race_labels, race_counts, color='skyblue')
    plt.xlabel('Race')
    plt.ylabel('Count of Deaths')
    plt.title('Mortality Rate by Race')
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, 'chart_1.png'))
    print(f"Saved chart to: {os.path.join(CHART_DIR, 'chart_1.png')}")

# Chart 2: Mortality rate by Gender and Race (Grouped Bar Chart)
if gender_race_data:
    groups = sorted(list(set(k[0] for k in gender_race_data.keys()))) # Unique races for grouping
    
    plt.figure(figsize=(12, 7))
    
    # Plotting requires careful handling of the structure. We will group by Race on the X-axis, and use Gender as the grouping variable within the bars.
    
    # Reorganize data for plotting: Group by Race, then iterate through genders
    race_gender_data = {}
    for (race, gender), rates in gender_race_data.items():
        if race not in race_gender_data:
            race_gender_data[race] = {}
        race_gender_data[race][gender] = rates

    plot_data = []
    for race in groups:
        gender_values = []
        for g in ['Male', 'Female']: # Assuming standard gender labels
            gender_values.append(race_gender_data[race].get(g, 0))
        plot_data.append(gender_values)

    x = np.arange(len(groups))
    width = 0.35
    
    plt.bar(x - width/2 * np.array([0, 1]), plot_data[0], width, label='Male')
    plt.bar(x + width/2 * np.array([0, 1]), plot_data[1], width, label='Female')
    
    plt.xlabel('Race')
    plt.ylabel('Mortality Rate')
    plt.title('Mortality Rate by Gender and Race')
    plt.xticks(x, groups)
    plt.legend(title='Gender')
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, 'chart_2.png'))
    print(f"Saved chart to: {os.path.join(CHART_DIR, 'chart_2.png')}")


# Chart 3: Age distribution of deaths (Histogram)
if age_counts:
    ages = list(age_counts.keys())
    counts = list(age_counts.values())
    
    plt.figure(figsize=(10, 6))
    plt.hist(ages, bins=np.arange(min(ages), max(ages) + 2) - 0.5, rwidth=0.8, color='lightcoral', edgecolor='black')
    plt.xlabel('Age')
    plt.ylabel('Count of Deaths')
    plt.title('Age Distribution of Deaths')
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, 'chart_3.png'))
    print(f"Saved chart to: {os.path.join(CHART_DIR, 'chart_3.png')}")