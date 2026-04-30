import csv
import os
import sys
from collections import defaultdict
from datetime import datetime

import numpy as np
import requests


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

HOURLY_HEADER = [
    "date", "hour", "day_of_week",
    "avg_hr", "max_hr", "min_hr",
    "hr_std", "steps", "hr_relative",
]

DAILY_HEADER = [
    "date", "day_of_week", "resting_hr", "total_steps",
    "total_sleep", "sleep_hours",
    "deep_ratio", "rem_ratio", "sleep_deficit",
    "sleep_start_time", "wake_time", "sleep_midpoint",
    "sleep_start_hour", "wake_hour",
    "avg_hr_day", "hr_std_day", "hr_deviation",
    "stress_index",
    "activity_load", "is_weekend",
    "mood_score", "productivity_score",
]


def fetch_fitbit_json(url, label, headers):
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to fetch {label}: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Fitbit returned invalid JSON for {label}") from exc

    if data.get("errors"):
        message = data["errors"][0].get("message", "Unknown Fitbit error")
        raise RuntimeError(f"Fitbit error for {label}: {message}")

    return data


def _parse_date_for_sort(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        return datetime.max


def _parse_hour_for_sort(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 99


def _clean_csv_value(value):
    if value is None:
        return ""

    return str(value).strip()


def repair_day(date=None, access_token=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        date = _clean_csv_value(date)

    if not access_token:
        raise ValueError("Access token required")

    headers = {"Authorization": f"Bearer {access_token}"}

    heart_intraday_url = (
        f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"
    )
    steps_intraday_url = (
        f"https://api.fitbit.com/1/user/-/activities/steps/date/{date}/1d/1min.json"
    )
    heart_daily_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d.json"
    sleep_url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"

    heart_intraday_data = fetch_fitbit_json(heart_intraday_url, "heart intraday", headers)
    steps_intraday_data = fetch_fitbit_json(steps_intraday_url, "steps intraday", headers)
    heart_daily_data = fetch_fitbit_json(heart_daily_url, "daily heart", headers)
    sleep_data = fetch_fitbit_json(sleep_url, "sleep", headers)

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

    resting_hr = (
        heart_daily_data.get("activities-heart", [{}])[0]
        .get("value", {})
        .get("restingHeartRate", 0)
    )

    day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()

    os.makedirs(DATA_DIR, exist_ok=True)

    hourly_file = os.path.join(DATA_DIR, "hourly_data.csv")

    rows_by_key = {}
    if os.path.exists(hourly_file):
        with open(hourly_file, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                row_date = _clean_csv_value(row[0]) if row else ""
                if not row_date or row_date == date:
                    continue

                row[0] = row_date
                hour = _clean_csv_value(row[1]) if len(row) > 1 else ""
                rows_by_key[(row_date, hour)] = row

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

        hr_relative = round(avg_hr - resting_hr, 2) if avg_hr != "" else ""

        rows_by_key[(date, str(hour))] = [
            date,
            hour,
            day_of_week,
            avg_hr if avg_hr == "" else round(avg_hr, 2),
            max_hr,
            min_hr,
            hr_std if hr_std == "" else round(hr_std, 2),
            steps,
            hr_relative,
        ]

    sorted_hourly_rows = sorted(
        rows_by_key.values(),
        key=lambda row: (_parse_date_for_sort(row[0]), _parse_hour_for_sort(row[1])),
    )

    with open(hourly_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HOURLY_HEADER)
        writer.writerows(sorted_hourly_rows)

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

            start = sleep_entry.get("startTime", "")
            end = sleep_entry.get("endTime", "")

            if start:
                start_times.append(start)

            if end:
                end_times.append(end)

            levels = sleep_entry.get("levels", {}).get("summary", {})
            deep_minutes += levels.get("deep", {}).get("minutes", 0)
            rem_minutes += levels.get("rem", {}).get("minutes", 0)

        if start_times:
            sleep_start_time = min(start_times)

        if end_times:
            wake_time = max(end_times)

    deep_ratio = deep_minutes / total_sleep if total_sleep else 0
    rem_ratio = rem_minutes / total_sleep if total_sleep else 0
    sleep_deficit = max(0, 480 - total_sleep)
    sleep_hours = round(total_sleep / 60, 2) if total_sleep else 0

    sleep_midpoint = ""
    sleep_start_hour = ""
    wake_hour = ""

    if sleep_start_time and wake_time:
        try:
            start_dt = datetime.fromisoformat(sleep_start_time.replace("Z", ""))
            end_dt = datetime.fromisoformat(wake_time.replace("Z", ""))

            midpoint = start_dt + (end_dt - start_dt) / 2
            sleep_midpoint = midpoint.time()

            sleep_start_hour = start_dt.hour
            wake_hour = end_dt.hour
        except ValueError:
            pass

    all_hr_values = [v for values in hourly_hr.values() for v in values]

    if all_hr_values:
        avg_hr_day = float(np.mean(all_hr_values))
        hr_std_day = float(np.std(all_hr_values))
    else:
        avg_hr_day = 0
        hr_std_day = 0

    hr_deviation = round(avg_hr_day - resting_hr, 2)
    stress_index = round(hr_std_day / avg_hr_day, 4) if avg_hr_day else 0
    activity_load = min(1, total_steps / 10000)
    is_weekend = 1 if day_of_week >= 5 else 0

    daily_file = os.path.join(DATA_DIR, "daily_data.csv")

    rows_by_date = {}
    existing_mood = ""
    existing_productivity = ""

    if os.path.exists(daily_file):
        with open(daily_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_date = _clean_csv_value(row.get("date", ""))
                if row_date == date:
                    existing_mood = row.get("mood_score", "") or existing_mood
                    existing_productivity = (
                        row.get("productivity_score", "") or existing_productivity
                    )
                    continue
                if row_date:
                    row["date"] = row_date
                    rows_by_date[row_date] = row

    new_daily_row = {
        "date": date,
        "day_of_week": day_of_week,
        "resting_hr": resting_hr,
        "total_steps": total_steps,
        "total_sleep": total_sleep,
        "sleep_hours": sleep_hours,
        "deep_ratio": round(deep_ratio, 3),
        "rem_ratio": round(rem_ratio, 3),
        "sleep_deficit": sleep_deficit,
        "sleep_start_time": sleep_start_time,
        "wake_time": wake_time,
        "sleep_midpoint": sleep_midpoint,
        "sleep_start_hour": sleep_start_hour,
        "wake_hour": wake_hour,
        "avg_hr_day": round(avg_hr_day, 2),
        "hr_std_day": round(hr_std_day, 2),
        "hr_deviation": hr_deviation,
        "stress_index": stress_index,
        "activity_load": round(activity_load, 2),
        "is_weekend": is_weekend,
        "mood_score": existing_mood,
        "productivity_score": existing_productivity,
    }

    rows_by_date[date] = new_daily_row
    sorted_daily_rows = [
        rows_by_date[row_date]
        for row_date in sorted(rows_by_date, key=_parse_date_for_sort)
    ]

    with open(daily_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DAILY_HEADER)
        writer.writeheader()

        for row in sorted_daily_rows:
            writer.writerow({key: row.get(key, "") for key in DAILY_HEADER})

    return {
        "date": date,
        "daily_file": daily_file,
        "hourly_file": hourly_file,
        "total_steps": total_steps,
        "sleep_hours": sleep_hours,
        "avg_hr_day": round(avg_hr_day, 2),
    }


if __name__ == "__main__":
    cli_date = sys.argv[1] if len(sys.argv) > 1 else None
    cli_token = sys.argv[2] if len(sys.argv) > 2 else None
    result = repair_day(cli_date, cli_token)
    print("Day repaired successfully:", result["date"])
    print("Updated:", result["daily_file"])
    print("Updated:", result["hourly_file"])
