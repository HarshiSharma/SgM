import pandas as pd
import json
import os

df = pd.read_csv("/opt/ml/processing/input/crew_data.csv")

def is_impostor(row):
    return (
        pd.isnull(row['name']) or 
        pd.isnull(row['role']) or 
        pd.isnull(row['age']) or 
        row['age'] > 100
    )

impostor_mask = df.apply(is_impostor, axis=1)
impostor_count = impostor_mask.sum()
clean_df = df[~impostor_mask]

os.makedirs("/opt/ml/processing/output", exist_ok=True)

# Save cleaned data
clean_df.to_csv("/opt/ml/processing/output/cleaned_crew.csv", index=False)

# Save impostor count for ConditionStep
with open("/opt/ml/processing/output/impostor_count.json", "w") as f:
    json.dump({"impostor_count": int(impostor_count)}, f)
