import requests
import csv
import os
import sys
from collections import defaultdict
import numpy as np
from datetime import datetime

date = sys.argv[1]
access_token = sys.argv[2]

headers = {"Authorization": f"Bearer {access_token}"}

# -------- API CALLS --------

heart_intraday_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"
steps_intraday_url = f"https://api.fitbit.com/1/user/-/activities/steps/date/{date}/1d/1min.json"
heart_daily_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d.json"
sleep_url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"

heart_intraday_data = requests.get(heart_intraday_url, headers=headers).json()
steps_intraday_data = requests.get(steps_intraday_url, headers=headers).json()
heart_daily_data = requests.get(heart_daily_url, headers=headers).json()
sleep_data = requests.get(sleep_url, headers=headers).json()

heart_intraday = heart_intraday_data.get("activities-heart-intraday", {}).get("dataset", [])
steps_intraday = steps_intraday_data.get("activities-steps-intraday", {}).get("dataset", [])

hourly_hr = defaultdict(list)
hourly_steps = defaultdict(int)

for entry in heart_intraday:
    hour = int(entry["time"].split(":")[0])
    hourly_hr[hour].append(entry["value"])

for entry in steps_intraday:
    hour = int(entry["time"].split(":")[0])
    hourly_steps[hour] += entry["value"]

resting_hr = heart_daily_data.get("activities-heart",[{}])[0].get("value",{}).get("restingHeartRate",0)

day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()

os.makedirs("data", exist_ok=True)

# -------- HOURLY FILE --------

hourly_file = "data/hourly_data.csv"

rows = []
if os.path.exists(hourly_file):
    with open(hourly_file, "r") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row[0] != date:
                rows.append(row)

with open(hourly_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "date","hour","day_of_week",
        "avg_hr","max_hr","min_hr",
        "hr_std","steps","hr_relative"
    ])

    for r in rows:
        writer.writerow(r)

    for hour in range(24):

        hr_values = hourly_hr.get(hour, [])
        steps = hourly_steps.get(hour, 0)

        if hr_values:
            avg_hr = float(np.mean(hr_values))
            max_hr = int(np.max(hr_values))
            min_hr = int(np.min(hr_values))
            hr_std = float(np.std(hr_values))
        else:
            avg_hr = ""
            max_hr = ""
            min_hr = ""
            hr_std = ""

        hr_relative = round(avg_hr - resting_hr,2) if avg_hr != "" else ""

        writer.writerow([
            date,
            hour,
            day_of_week,
            avg_hr if avg_hr == "" else round(avg_hr,2),
            max_hr,
            min_hr,
            hr_std if hr_std == "" else round(hr_std,2),
            steps,
            hr_relative
        ])

# -------- DAILY FEATURES --------

total_steps = sum(hourly_steps.values())

total_sleep = 0
deep_minutes = 0
rem_minutes = 0
sleep_start_time = ""
wake_time = ""

sleep_sessions = sleep_data.get("sleep", [])

if sleep_sessions:

    start_times = []
    end_times = []

    for sleep_entry in sleep_sessions:

        total_sleep += sleep_entry.get("minutesAsleep", 0)

        start = sleep_entry.get("startTime","")
        end = sleep_entry.get("endTime","")

        if start:
            start_times.append(start)

        if end:
            end_times.append(end)

        levels = sleep_entry.get("levels",{}).get("summary",{})

        deep_minutes += levels.get("deep",{}).get("minutes",0)
        rem_minutes += levels.get("rem",{}).get("minutes",0)

    if start_times:
        sleep_start_time = min(start_times)

    if end_times:
        wake_time = max(end_times)

# ----- sleep calculations -----

deep_ratio = deep_minutes / total_sleep if total_sleep else 0
rem_ratio = rem_minutes / total_sleep if total_sleep else 0
sleep_deficit = max(0, 480 - total_sleep)

sleep_hours = round(total_sleep / 60,2) if total_sleep else 0

sleep_midpoint = ""
sleep_start_hour = ""
wake_hour = ""

if sleep_start_time and wake_time:
    try:
        start_dt = datetime.fromisoformat(sleep_start_time.replace("Z",""))
        end_dt = datetime.fromisoformat(wake_time.replace("Z",""))

        midpoint = start_dt + (end_dt - start_dt)/2
        sleep_midpoint = midpoint.time()

        sleep_start_hour = start_dt.hour
        wake_hour = end_dt.hour
    except:
        pass

# -------- HR FEATURES --------

all_hr_values = [v for sub in hourly_hr.values() for v in sub]

if all_hr_values:
    avg_hr_day = float(np.mean(all_hr_values))
    hr_std_day = float(np.std(all_hr_values))
else:
    avg_hr_day = 0
    hr_std_day = 0

hr_deviation = round(avg_hr_day - resting_hr,2)

stress_index = round(hr_std_day / avg_hr_day,4) if avg_hr_day else 0

# -------- ACTIVITY --------

activity_load = min(1, total_steps / 10000)

is_weekend = 1 if day_of_week >= 5 else 0

# -------- DAILY FILE --------

daily_file = "data/daily_data.csv"

file_exists = os.path.exists(daily_file)

with open(daily_file, "a", newline="") as f:

    writer = csv.writer(f)

    if not file_exists:
        writer.writerow([
        "date","day_of_week","resting_hr","total_steps",
        "total_sleep","sleep_hours",
        "deep_ratio","rem_ratio","sleep_deficit",
        "sleep_start_time","wake_time","sleep_midpoint",
        "sleep_start_hour","wake_hour",
        "avg_hr_day","hr_std_day","hr_deviation",
        "stress_index",
        "activity_load","is_weekend",
        "mood_score","productivity_score"
        ])

    writer.writerow([
        date,
        day_of_week,
        resting_hr,
        total_steps,
        total_sleep,
        sleep_hours,
        round(deep_ratio,3),
        round(rem_ratio,3),
        sleep_deficit,
        sleep_start_time,
        wake_time,
        sleep_midpoint,
        sleep_start_hour,
        wake_hour,
        round(avg_hr_day,2),
        round(hr_std_day,2),
        hr_deviation,
        stress_index,
        round(activity_load,2),
        is_weekend,
        "",
        ""
    ])

print("Day repaired successfully:", date)