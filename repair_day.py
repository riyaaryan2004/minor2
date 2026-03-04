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

heart_intraday = heart_intraday_data["activities-heart-intraday"]["dataset"]
steps_intraday = steps_intraday_data["activities-steps-intraday"]["dataset"]

hourly_hr = defaultdict(list)
hourly_steps = defaultdict(int)

for entry in heart_intraday:
    hour = int(entry["time"].split(":")[0])
    hourly_hr[hour].append(entry["value"])

for entry in steps_intraday:
    hour = int(entry["time"].split(":")[0])
    hourly_steps[hour] += entry["value"]

resting_hr = heart_daily_data["activities-heart"][0]["value"].get("restingHeartRate", 0)

day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()

os.makedirs("data", exist_ok=True)

# -------- HOURLY FILE --------

hourly_file = "data/hourly_data.csv"

rows = []
if os.path.exists(hourly_file):
    with open(hourly_file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
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
            avg_hr = np.mean(hr_values)
            max_hr = np.max(hr_values)
            min_hr = np.min(hr_values)
            hr_std = np.std(hr_values)
        else:
            avg_hr = np.nan
            max_hr = np.nan
            min_hr = np.nan
            hr_std = np.nan

        hr_relative = avg_hr - resting_hr if not np.isnan(avg_hr) else np.nan

        writer.writerow([
            date,
            hour,
            day_of_week,
            round(avg_hr,2) if not np.isnan(avg_hr) else "",
            int(max_hr) if not np.isnan(max_hr) else "",
            int(min_hr) if not np.isnan(min_hr) else "",
            round(hr_std,2) if not np.isnan(hr_std) else "",
            steps,
            round(hr_relative,2) if not np.isnan(hr_relative) else ""
        ])

# -------- DAILY FILE --------

total_steps = sum(hourly_steps.values())

total_sleep = 0
deep_minutes = 0
rem_minutes = 0
sleep_start_time = ""
wake_time = ""

if "sleep" in sleep_data and len(sleep_data["sleep"]) > 0:
    sleep_entry = sleep_data["sleep"][0]
    total_sleep = sleep_entry.get("minutesAsleep", 0)
    sleep_start_time = sleep_entry.get("startTime","")
    wake_time = sleep_entry.get("endTime","")

    if "levels" in sleep_entry:
        levels = sleep_entry["levels"]["summary"]
        deep_minutes = levels.get("deep", {}).get("minutes", 0)
        rem_minutes = levels.get("rem", {}).get("minutes", 0)

deep_ratio = deep_minutes / total_sleep if total_sleep else 0
rem_ratio = rem_minutes / total_sleep if total_sleep else 0
sleep_deficit = 480 - total_sleep

all_hr_values = [val for sublist in hourly_hr.values() for val in sublist]

avg_hr_day = np.mean(all_hr_values) if all_hr_values else 0
hr_std_day = np.std(all_hr_values) if all_hr_values else 0

activity_load = total_steps / 10000

daily_file = "data/daily_data.csv"

rows = []
if os.path.exists(daily_file):
    with open(daily_file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row[0] != date:
                rows.append(row)

with open(daily_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "date","day_of_week","resting_hr","total_steps",
        "total_sleep","deep_ratio","rem_ratio","sleep_deficit",
        "sleep_start_time","wake_time",
        "avg_hr_day","hr_std_day","activity_load",
        "mood_score","productivity_score"
    ])

    for r in rows:
        writer.writerow(r)

    writer.writerow([
        date,
        day_of_week,
        resting_hr,
        total_steps,
        total_sleep,
        round(deep_ratio,3),
        round(rem_ratio,3),
        sleep_deficit,
        sleep_start_time,
        wake_time,
        round(avg_hr_day,2),
        round(hr_std_day,2),
        round(activity_load,2),
        "",
        ""
    ])

print("Day repaired successfully:", date)