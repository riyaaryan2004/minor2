import pandas as pd
import os
import numpy as np
import joblib

from sklearn.preprocessing import StandardScaler

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, "data", "daily_data.csv")
save_dir = os.path.join(BASE_DIR, "saved_models")

print("DATA PATH:", data_path)
print("EXISTS:", os.path.exists(data_path))

# ---------------- LOAD DATA ----------------
df = pd.read_csv(data_path)

if df.empty:
    raise ValueError("Dataset is empty")

print("Original Shape:", df.shape)

# Sort by date
df = df.sort_values("date")

# Source tagging (real vs synthetic)
df["source"] = df["date"].apply(lambda x: "real" if x >= "2026-03-01" else "synthetic")

# ---------------- FEATURE ENGINEERING ----------------

# Sleep efficiency
df["sleep_efficiency"] = df["total_sleep"] / df["sleep_hours"].replace(0, 1)

# HR stress ratio
df["hr_stress_ratio"] = df["avg_hr_day"] / (df["resting_hr"] + 1)

# Preserve raw stress (VERY IMPORTANT)
df["stress_index_raw"] = df["stress_index"]

# Log transform for model
df["stress_index_log"] = np.log1p(df["stress_index_raw"])

# Interaction (use log version only)
df["stress_sleep_interaction"] = df["stress_index_log"] * df["sleep_deficit"]

# Steps scaling
df["steps_scaled"] = df["total_steps"] / 10000

# ---------------- CLEANING ----------------

df = df.drop(columns=[
    "date",
    "sleep_start_time",
    "wake_time",
    "sleep_midpoint"
], errors="ignore")

# ---------------- FEATURE SELECTION ----------------

selected_features = [
    "sleep_efficiency",
    "stress_index_log",
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
    raise ValueError("Missing required features")

X = df[selected_features]

# ---------------- TARGETS ----------------

y_mood = df["mood_score"].fillna(df["mood_score"].mean()).clip(1, 10)
y_prod = df["productivity_score"].fillna(df["productivity_score"].mean()).clip(1, 10)

print("\nNaN check in targets:")
print("Mood NaN:", y_mood.isna().sum())
print("Prod NaN:", y_prod.isna().sum())

print("\nFinal Features Used:", list(X.columns))

# ---------------- DEBUG / ANALYSIS ----------------

print("\nCorrelation with Mood:")
print(X.corrwith(y_mood).sort_values(ascending=False))

print("\nFeature Correlation Matrix:")
print(X.corr())

# ---------------- TRAIN TEST SPLIT (TIME BASED) ----------------

split_index = int(len(X) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train_mood = y_mood.iloc[:split_index]
y_test_mood = y_mood.iloc[split_index:]

y_train_prod = y_prod.iloc[:split_index]
y_test_prod = y_prod.iloc[split_index:]

# ---------------- SCALING (FIXED - NO DATA LEAKAGE) ----------------

scaler = StandardScaler()

X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=selected_features)
X_test = pd.DataFrame(scaler.transform(X_test), columns=selected_features)

# Save scaler
os.makedirs(save_dir, exist_ok=True)
joblib.dump(scaler, os.path.join(save_dir, "scaler.pkl"))

# ---------------- SAMPLE WEIGHTS ----------------

sample_weight = df["source"].apply(lambda x: 2 if x == "real" else 1)
w_train = sample_weight.iloc[:split_index]

# ---------------- FINAL LOGS ----------------

print("\nTraining samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

print("\nData preprocessing completed successfully!")

feature_names = selected_features