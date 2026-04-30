import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_alerts(date=None):
    try:
        df = pd.read_csv(os.path.join(BASE_DIR, "data", "daily_data.csv"))
        if date:
            df = df[df["date"] == date]
            if df.empty:
                return ["No data available for selected date"]
        row = df.tail(1).iloc[0]
    except:
        return ["No data available"]

    alerts = []

    resting = row["resting_hr"]
    avg_hr = row["avg_hr_day"]
    hr_std = row["hr_std_day"]

    # ---- HEART RATE ANOMALY ----

    # Case 1: Avg HR too high
    if avg_hr > resting + 20:
        alerts.append("Heart rate significantly elevated")

    # Case 2: High variability (unstable HR)
    elif hr_std > 15:
        alerts.append("Irregular heart rate pattern detected")

    # Case 3: Slight elevation
    elif avg_hr > resting + 10:
        alerts.append("Slightly elevated heart rate")

    # ---- NO ANOMALY ----
    if not alerts:
        alerts.append("Heart rate normal")

    return alerts