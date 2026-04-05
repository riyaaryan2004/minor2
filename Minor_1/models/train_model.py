import pandas as pd
import os
import numpy as np
import joblib

# Path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, "data", "daily_data.csv")

print("DATA PATH:", data_path)
print("EXISTS:", os.path.exists(data_path))

df = pd.read_csv(data_path)
print("Original Shape:", df.shape)

# Sort by date
df = df.sort_values("date")

# Source column
df["source"] = df["date"].apply(lambda x: "real" if x >= "2026-03-01" else "synthetic")

# ---------------- FEATURE ENGINEERING ----------------

df["sleep_efficiency"] = df["total_sleep"] / df["sleep_hours"].replace(0, 1)
df["hr_stress_ratio"] = df["avg_hr_day"] / (df["resting_hr"] + 1)

# SAVE RAW STRESS (important for consistency later)
df["stress_index_raw"] = df["stress_index"]

# Log transform
df["stress_index"] = np.log1p(df["stress_index"])

# Interaction
df["stress_sleep_interaction"] = df["stress_index"] * df["sleep_deficit"]

# Steps scaling (keep simple)
df["steps_scaled"] = df["total_steps"] / 10000

# ----------------------------------------------------

# Drop unnecessary columns
df = df.drop(columns=[
    "date",
    "sleep_start_time",
    "wake_time",
    "sleep_midpoint"
])

# Remove missing
# Features
selected_features = [
    "sleep_efficiency",
    "stress_index",
    "activity_load",
    "hr_stress_ratio",
    "sleep_deficit",
    "steps_scaled",
    "stress_sleep_interaction"
]

# Safety check
missing_cols = [col for col in selected_features if col not in df.columns]
if missing_cols:
    print("Missing columns:", missing_cols)
    raise ValueError("Missing columns")

X = df[selected_features]
feature_names = selected_features

# Targets
y_mood = df["mood_score"].fillna(df["mood_score"].mean()).clip(1, 10)
y_prod = df["productivity_score"].fillna(df["productivity_score"].mean()).clip(1, 10)

print("\nNaN check in targets:")
print("Mood NaN:", y_mood.isna().sum())
print("Prod NaN:", y_prod.isna().sum())

print("\nFinal Features Used:", list(X.columns))

# ---------------- DEBUG (VERY USEFUL) ----------------
print("\nCorrelation with Mood:")
print(X.corrwith(y_mood).sort_values(ascending=False))

print("\nFeature Correlation Matrix:")
print(X.corr())
# ---------------------------------------------------

# ---------------- SCALING (FIXED) ----------------
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=selected_features)

save_dir = os.path.join(BASE_DIR, "saved_models")

joblib.dump(scaler, os.path.join(save_dir, "scaler.pkl"))

# Time split
split_index = int(len(X_scaled) * 0.8)

X_train = X_scaled.iloc[:split_index]
X_test = X_scaled.iloc[split_index:]

y_train_mood = y_mood.iloc[:split_index]
y_test_mood = y_mood.iloc[split_index:]

y_train_prod = y_prod.iloc[:split_index]
y_test_prod = y_prod.iloc[split_index:]

# Sample weights
sample_weight = df["source"].apply(lambda x: 2 if x == "real" else 1)
w_train = sample_weight.iloc[:split_index]

print("\nTraining samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

print("\nData preprocessing completed!")