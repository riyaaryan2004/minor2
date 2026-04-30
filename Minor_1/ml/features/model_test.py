
import csv
from datetime import datetime
import os
import sys
import pandas as pd

# -----------------------------
# BASE DIR (project root)
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# 🔥 import prediction (FIXED)
from ml.features.predict_day import predict_day

# -----------------------------
# FILE PATH (correct location)
# -----------------------------
file_name = os.path.join(BASE_DIR, "data", "evaluation_results.csv")
file_exists = os.path.isfile(file_name)

# ---- USER NAME ----
user_name = input("Enter user name: ")

# ---- TODAY DATE AUTO ----
today_date = datetime.now().strftime("%Y-%m-%d")

# ---- GET PREDICTION ----
df = pd.read_csv(os.path.join(BASE_DIR, "data", "daily_data.csv"))
row = df.tail(1).iloc[0]
mood_pred, prod_pred = predict_day(row)

mood_pred = round(mood_pred, 2)
prod_pred = round(prod_pred, 2)

print(f"\n--- Date: {today_date} ---")
print("Predicted Mood:", mood_pred)
print("Predicted Productivity:", prod_pred)

# ---- USER INPUT ----
actual_mood = float(input("Actual Mood (0-10): "))
actual_prod = float(input("Actual Productivity (0-10): "))

# ---- ERROR ----
mood_error = round(abs(actual_mood - mood_pred), 2)
prod_error = round(abs(actual_prod - prod_pred), 2)

# -----------------------------
# ENSURE DATA FOLDER EXISTS
# -----------------------------
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ---- SAVE ----
with open(file_name, "a", newline="") as file:
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow([
            "Timestamp", "User", "Date",
            "Actual Mood", "Predicted Mood", "Mood Error",
            "Actual Productivity", "Predicted Productivity", "Productivity Error"
        ])

    writer.writerow([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        user_name,
        today_date,
        actual_mood, mood_pred, mood_error,
        actual_prod, prod_pred, prod_error
    ])

print("\n✅ Today’s data saved successfully")