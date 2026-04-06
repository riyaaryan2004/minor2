import pandas as pd
import os
import numpy as np
import joblib

# Path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, "final_dataset.csv")

print("DATA PATH:", data_path)
print("EXISTS:", os.path.exists(data_path))

df = pd.read_csv(data_path)
print("Original Shape:", df.shape)

# Sort by date
df = df.sort_values("date")

# ✅ Source column
df["source"] = df["date"].apply(lambda x: "real" if x >= "2026-03-01" else "synthetic")

# ---------------- FEATURE ENGINEERING ----------------

# Sleep efficiency (FIXED)
df["sleep_efficiency"] = df["sleep_hours"] / 8

# Stress already exists → just safe transform
df["stress_index"] = np.log1p(df["stress_index"].clip(lower=0))

# Interaction
df["stress_sleep_interaction"] = df["stress_index"] * df["sleep_deficit"]

# Steps scaling
df["steps_scaled"] = df["total_steps"] / 10000

# Recovery score
df["recovery_score"] = df["sleep_hours"] / (df["activity_load"] + 1)

# Fatigue index
df["fatigue_index"] = df["sleep_deficit"] + (df["activity_load"] / 500)

# Activity trend
df["activity_trend"] = df["total_steps"] - df["steps_prev1"]

# Sleep variation (handle NaN)
df["sleep_variation"] = df.groupby("Id")["sleep_hours"].transform(
    lambda x: x.rolling(3).std()
).fillna(0)

# ----------------------------------------------------

# Drop unnecessary columns (only if present)
drop_cols = [
    "sleep_start_time",
    "wake_time",
    "sleep_midpoint"
]

df = df.drop(columns=[col for col in drop_cols if col in df.columns])

# Remove missing
df = df.dropna()
print("Clean Shape:", df.shape)

# Features (UPDATED)
selected_features = [
    "sleep_efficiency",
    "stress_index",
    "activity_load",
    "sleep_deficit",
    "steps_scaled",
    "stress_sleep_interaction",
    "recovery_score",
    "fatigue_index",
    "activity_trend",
    "sleep_variation"
]

# Safety check
missing_cols = [col for col in selected_features if col not in df.columns]
if missing_cols:
    print("Missing columns:", missing_cols)
    raise ValueError("Missing columns")

X = df[selected_features]
feature_names = selected_features

# Targets
y_mood = df["mood_score"].clip(1, 10)
y_prod = df["productivity_score"].clip(1, 10)

print("\nFinal Features Used:", list(X.columns))

# ---------------- DEBUG ----------------
print("\nCorrelation with Mood:")
print(X.corrwith(y_mood).sort_values(ascending=False))

print("\nFeature Correlation Matrix:")
print(X.corr())
# ---------------------------------------------------

# ---------------- SCALING ----------------
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=selected_features)

save_dir = os.path.join(BASE_DIR, "saved_models")
os.makedirs(save_dir, exist_ok=True)

joblib.dump(scaler, os.path.join(save_dir, "scaler.pkl"))

# ---------------- SPLIT ----------------
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

print("\n✅ Data preprocessing completed!")