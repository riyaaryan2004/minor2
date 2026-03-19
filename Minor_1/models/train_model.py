import pandas as pd
import os

# Path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, "data", "daily_data.csv")

# Debug (helps if path breaks)
print("DATA PATH:", data_path)
print("EXISTS:", os.path.exists(data_path))

df = pd.read_csv(data_path)

print("Original Shape:", df.shape)

# Sort by date
df = df.sort_values("date")

# Feature Engineering (NEW)
df["sleep_efficiency"] = df["total_sleep"] / (df["sleep_hours"] + 1)
df["hr_stress_ratio"] = df["avg_hr_day"] / (df["resting_hr"] + 1)

# Drop unnecessary columns
df = df.drop(columns=[
    "date",
    "sleep_start_time",
    "wake_time",
    "sleep_midpoint"
])

# Remove missing
df = df.dropna()

print("Clean Shape:", df.shape)

# 🎯 SELECTED FEATURES (KEEPING YOUR CHOICE — just validating existence)
selected_features = [
    "hr_std_day",
    "day_of_week",
    "total_steps",
    "avg_hr_day",
    "activity_load",
    "stress_index"
]

# Safety check (VERY IMPORTANT)
missing_cols = [col for col in selected_features if col not in df.columns]
if missing_cols:
    print("❌ Missing columns:", missing_cols)
    raise ValueError("Some selected features are missing in dataset")

X = df[selected_features]

# Targets
y_mood = df["mood_score"].clip(1, 10)
y_prod = df["productivity_score"].clip(1, 10)

feature_names = X.columns

print("\nFinal Features Used:", list(feature_names))

# Correlation check (helps explain results)
print("\nCorrelation with Mood:")
print(X.corrwith(y_mood).sort_values(ascending=False))

# Time-based split
split_index = int(len(X) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train_mood = y_mood.iloc[:split_index]
y_test_mood = y_mood.iloc[split_index:]

y_train_prod = y_prod.iloc[:split_index]
y_test_prod = y_prod.iloc[split_index:]

print("\nTraining samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

print("Train shape:", X_train.shape)
print("Test shape:", X_test.shape)