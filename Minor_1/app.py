import sys
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FEATURES_DIR = os.path.join(BASE_DIR, "features")

sys.path.append(FEATURES_DIR)

from flask import Flask,redirect,request
import requests
import base64
import csv
import os
from datetime import datetime
from collections import defaultdict
import numpy as np
from flask_cors import CORS

# app is the complete web server
# isi app par routes banenge
app = Flask(__name__)

CORS(app)

CLIENT_ID = "23TXMK"
CLIENT_SECRET = "b19bed40782c38915f7a78687262612b"
REDIRECT_URI = "http://localhost:5000/callback"

# test endpoint to verify the server is running
@app.route("/")
def home():
    return "Fitbit Mood Data Collector Running"

# Login route
@app.route("/login")
def login():
    auth_url = (
        "https://www.fitbit.com/oauth2/authorize"
        f"?response_type=code&client_id={CLIENT_ID}"
        "&scope=heartrate activity sleep"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

# Callback route
@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return {"error": "No authorization code received"}, 400

    token_url = "https://api.fitbit.com/oauth2/token"

    auth_header = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code != 200:
        return {"error": "Token exchange failed"}, 400

    access_token = response.json()["access_token"]

    # SAVE TOKEN (inside function)
    with open("token.txt", "w") as f:
        f.write(access_token)

    # RETURN INSIDE FUNCTION
    return redirect("/collect")

# Data Collection Route
@app.route("/collect")
def collect():
    with open("token.txt", "r") as f:
        access_token = f.read().strip()

    if not access_token:
        return {"error": "Missing access token"}, 400

    headers = {"Authorization": f"Bearer {access_token}"}

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    day_of_week = now.weekday()

    # ---------------- INTRADAY HEART RATE ----------------
    heart_intraday_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{today}/1d/1min.json"
    heart_intraday_data = requests.get(heart_intraday_url, headers=headers).json()

    # ---------------- INTRADAY STEPS ----------------
    steps_intraday_url = f"https://api.fitbit.com/1/user/-/activities/steps/date/{today}/1d/1min.json"
    steps_intraday_data = requests.get(steps_intraday_url, headers=headers).json()

    # ---------------- DAILY HEART SUMMARY ----------------
    heart_daily_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{today}/1d.json"
    heart_daily_data = requests.get(heart_daily_url, headers=headers).json()

    # ---------------- SLEEP DATA ----------------
    sleep_url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{today}.json"
    sleep_data = requests.get(sleep_url, headers=headers).json()

    # ===================== HOURLY PROCESSING =====================

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
    
    os.makedirs("data", exist_ok=True)
    hourly_file = "data/hourly_data.csv"

    existing_rows = []
    if os.path.exists(hourly_file):
        with open(hourly_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row:
                    continue
                if row[0] != today:
                    existing_rows.append(row)

    with open(hourly_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "date","hour","day_of_week",
            "avg_hr","max_hr","min_hr",
            "hr_std","steps","hr_relative"
        ])

        for row in existing_rows:
            writer.writerow(row)

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
                today,
                hour,
                day_of_week,
                round(avg_hr,2) if not np.isnan(avg_hr) else "",
                int(max_hr) if not np.isnan(max_hr) else "",
                int(min_hr) if not np.isnan(min_hr) else "",
                round(hr_std,2) if not np.isnan(hr_std) else "",
                steps,
                round(hr_relative,2) if not np.isnan(hr_relative) else ""
            ])

    # ===================== DAILY SUMMARY PROCESSING =====================

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

    sleep_midpoint = ""

    if sleep_start_time and wake_time:
        try:
            start_dt = datetime.fromisoformat(sleep_start_time.replace("Z",""))
            end_dt = datetime.fromisoformat(wake_time.replace("Z",""))
            midpoint = start_dt + (end_dt - start_dt)/2
            sleep_midpoint = midpoint.time()
        except:
            sleep_midpoint = ""

    # Safe calculations
    deep_ratio = (deep_minutes / total_sleep) if total_sleep else 0
    rem_ratio = (rem_minutes / total_sleep) if total_sleep else 0
    sleep_deficit = max(0, 480 - total_sleep)

    sleep_hours = round(total_sleep / 60, 2) if total_sleep else 0

    # circadian features
    sleep_start_hour = ""
    wake_hour = ""

    try:
        if sleep_start_time:
            sleep_start_hour = datetime.fromisoformat(sleep_start_time.replace("Z","")).hour
        if wake_time:
            wake_hour = datetime.fromisoformat(wake_time.replace("Z","")).hour
    except:
        pass

    # HR aggregation (moved outside sleep block to avoid crash)
    all_hr_values = [val for sublist in hourly_hr.values() for val in sublist]

    if all_hr_values:
        avg_hr_day = float(np.mean(all_hr_values))
        hr_std_day = float(np.std(all_hr_values))
    else:
        avg_hr_day = 0
        hr_std_day = 0

    hr_deviation = round(avg_hr_day - resting_hr, 2)

    # stress signal
    stress_index = round(hr_std_day / avg_hr_day, 4) if avg_hr_day else 0

    # Activity normalization
    activity_load = min(1, total_steps / 10000)

    is_weekend = 1 if day_of_week >= 5 else 0

    daily_file = "data/daily_data.csv"

    existing_daily = []
    if os.path.exists(daily_file):
        with open(daily_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)

            for row in reader:
                if not row:
                    continue

                while len(row) < 22:
                    row.append("")

                if row[0] != today:
                    existing_daily.append(row)

    with open(daily_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

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

        for row in existing_daily:
            writer.writerow(row)

        writer.writerow([
            today,
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
    return {"status": "Hourly and Daily data collected successfully"}


# ===================== RATING ROUTE =====================

@app.route("/rate")
def rate():
    mood = request.args.get("mood")
    productivity = request.args.get("productivity")

    if not mood or not productivity:
        return {"error": "Provide mood and productivity"}, 400

    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = "data/daily_data.csv"

    if not os.path.exists(daily_file):
        return {"error": "Collect data first"}, 400

    updated_rows = []

    with open(daily_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)

        for row in reader:
            if not row:
                continue

            while len(row) < 22:
                row.append("")

            if row[0] == today:
                row[-2] = mood
                row[-1] = productivity

            updated_rows.append(row)

    with open(daily_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)

    return {"status": "Mood and productivity recorded successfully"}

# ===================== PREDICT ROUTE =====================
@app.route("/predict")
def predict():
    from features.predict_day import predict_day
    import pandas as pd
    import os

    mood, prod = predict_day()

    df = pd.read_csv(os.path.join("data", "daily_data.csv"))
    latest = df.iloc[-1]

    sleep = latest["sleep_hours"]
    stress = latest["stress_index"]
    steps = latest["total_steps"]
    resting = latest["resting_hr"]
    avg_hr = latest["avg_hr_day"]

    # ===================== 1. TODAY INSIGHT =====================
    if stress > 0.18:
        summary = "Your body is under noticeable stress today."
    elif sleep < 5:
        summary = "Your recovery is low due to insufficient sleep."
    else:
        summary = "Your overall condition looks fairly stable today."

    # ===================== 2. METRICS =====================
    metrics = {
        "steps": int(steps),
        "avg_hr": round(avg_hr, 1),
        "resting_hr": int(resting),
        "sleep": round(sleep, 2),
        "stress": round(stress, 3)   
    }

    # ===================== 3. WHAT IT MEANS =====================
    meaning = []

    # Heart rate
    if avg_hr > resting + 10:
        meaning.append("Heart rate is elevated compared to your baseline, indicating internal stress or fatigue.")
    else:
        meaning.append("Heart rate is within a normal range.")

    # Sleep
    if sleep < 5:
        meaning.append("Sleep duration is low, which reduces recovery and focus.")
    else:
        meaning.append("Sleep is within a reasonable range for recovery.")

    # Steps
    if steps < 3000:
        meaning.append("Low activity may reduce energy levels and natural stress regulation.")
    else:
        meaning.append("Activity level is helping maintain energy balance.")

    # ===================== 4. WHY ACTION =====================
    if stress > 0.18 and sleep < 5:
        reasoning = "High stress combined with low sleep means your body is not in a recovery state."
    elif stress > 0.18:
        reasoning = "Elevated stress suggests your body needs regulation and rest."
    elif sleep < 5:
        reasoning = "Low sleep suggests reduced recovery, so energy levels may drop."
    else:
        reasoning = "Your metrics are relatively balanced."

    # ===================== 5. ACTIVITY =====================
    if stress > 0.18:
        activity = "Take a 15–20 min walk and keep workload light."
        activity_why = "Light movement helps reduce stress and stabilizes heart rate without overloading your body."
    elif sleep < 5:
        activity = "Keep tasks light and prioritize recovery today."
        activity_why = "Low sleep reduces recovery capacity, so avoiding overload prevents burnout."
    elif steps < 3000:
        activity = "Increase movement slightly — even a short walk will help."
        activity_why = "Movement improves circulation, boosts mood, and regulates stress."
    else:
        activity = "Maintain your current routine."
        activity_why = "Your body is already in a stable state."

    # ===================== 6. MOVIE WHY =====================
    if mood < 4:
        movie_why = "Low mood detected — light or uplifting content can help improve emotional state."
    elif stress > 0.18:
        movie_why = "High stress — calming content helps reduce mental load."
    else:
        movie_why = "Balanced state — entertainment can be used for relaxation."

    # ===================== 7. TRENDS =====================
    trends = {}

    if len(df) >= 2:
        prev = df.iloc[-2]

        def trend(val, unit=""):
            arrow = "↑" if val > 0 else "↓" if val < 0 else "→"
            return f"{arrow} {round(abs(val),2)}{unit}"

        trends = {
            "sleep": trend(sleep - prev["sleep_hours"], " hrs"),
            "stress": trend(stress - prev["stress_index"]),
            "steps": trend(steps - prev["total_steps"])
        }
    else:
        trends = {
            "sleep": "No data",
            "stress": "No data",
            "steps": "No data"
        }

    # ===================== FINAL RESPONSE =====================
    return {
        "today_insight": summary,
        "metrics": metrics,
        "meaning": meaning,
        "reasoning": reasoning,
        "activity": {
            "suggestion": activity,
            "why": activity_why
        },
        "movie": {
            "why": movie_why
        },
        "trends": trends,
        "mood": round(mood, 2),
        "productivity": round(prod, 2)
    }
    
# ===================== MOVIES ROUTE =====================
@app.route("/movies")
def movies():
    from features.predict_day import predict_day
    from features.movie_recommendor import recommend_movies

    mood, prod = predict_day()

    movies = recommend_movies()

    # reasoning
    if mood < 4:
        reason = "Your mood is low, so uplifting or light content can help improve emotional state."
    elif prod < 4:
        reason = "Low productivity suggests mental fatigue, so light entertainment helps recovery."
    elif mood >= 7 and prod >= 7:
        reason = "High energy state — engaging content matches your focus."
    else:
        reason = "Balanced state — movies can be used for relaxation."

    return {
        "why": reason,
        "movies": movies
    }
    
# ===================== ACTIVITY ROUTE =====================
@app.route("/activity")
def activity():
    from features.predict_day import predict_day
    from features.activity_suggestion import get_activity_suggestions
    import pandas as pd
    import os

    mood, prod = predict_day()

    df = pd.read_csv(os.path.join("data", "daily_data.csv"))
    row = df.tail(1).iloc[0]

    suggestions = get_activity_suggestions(row, mood, prod, row["stress_index"])

    # pick top suggestion
    suggestion = suggestions[0] if suggestions else "Maintain your routine."

    # reasoning (simple but powerful)
    if row["stress_index"] > 0.18:
        why = "Your stress is high, so light activity helps regulate it."
    elif row["sleep_hours"] < 5:
        why = "Low sleep means your body needs recovery, not overload."
    elif row["total_steps"] < 3000:
        why = "Low movement reduces energy, so activity helps boost it."
    else:
        why = "Your metrics are stable, so maintaining routine is ideal."

    return {
        "suggestion": suggestion,
        "why": why
    }
       
# ===================== ALERTS ROUTE =====================
@app.route("/alerts")
def alerts():
    from features.alerts import get_alerts
    import pandas as pd
    import os

    df = pd.read_csv(os.path.join("data", "daily_data.csv"))
    row = df.tail(1).iloc[0]

    alerts = get_alerts()

    detailed_alerts = []

    for alert in alerts:

        if "significantly elevated" in alert:
            detailed_alerts.append({
                "issue": "High Heart Rate",
                "why": "Your average heart rate is much higher than your resting level, indicating strong stress or fatigue.",
                "action": "Avoid intense activity and focus on recovery (rest, hydration, light movement)."
            })

        elif "Irregular heart rate" in alert:
            detailed_alerts.append({
                "issue": "Irregular Heart Pattern",
                "why": "High heart rate variability suggests unstable physiological state.",
                "action": "Take it easy and avoid overexertion today."
            })

        elif "Slightly elevated" in alert:
            detailed_alerts.append({
                "issue": "Slightly Elevated Heart Rate",
                "why": "Your heart rate is above normal, possibly due to stress or low recovery.",
                "action": "Take short breaks and avoid continuous workload."
            })

        else:
            detailed_alerts.append({
                "issue": "Normal",
                "why": "Your heart rate is within a healthy range.",
                "action": "Maintain your routine."
            })

    return {
        "alerts": detailed_alerts
    }
    
# ===================== HEART RATE ROUTE =====================

@app.route("/hr-data")
def hr_data():
    import pandas as pd
    import os

    df = pd.read_csv(os.path.join("data", "hourly_data.csv"))

    # take latest date
    latest_date = df["date"].max()

    df = df[df["date"] == latest_date]

    # remove missing HR rows
    df = df.dropna(subset=["avg_hr"])

    result = []

    for _, row in df.iterrows():
        result.append({
            "hour": int(row["hour"]),
            "hr": round(row["avg_hr"], 1)
        })

    return sorted(result, key=lambda x: x["hour"])

from features.hr_live import get_intraday_hr
from datetime import datetime

@app.route("/hr-live")
def hr_live():
    with open("token.txt", "r") as f:
        ACCESS_TOKEN = f.read().strip()

    today = datetime.now().strftime("%Y-%m-%d")

    data = get_intraday_hr(ACCESS_TOKEN, today)

    return data

# ===================== HEART RATE MINUTE GRAPH =====================
@app.route("/hr-minute")
def hr_minute():
    from features.hr_live import get_intraday_hr
    import pandas as pd
    import os

    # read token
    with open("token.txt", "r") as f:
        ACCESS_TOKEN = f.read().strip()

    # 🔥 get latest date from dataset
    df = pd.read_csv(os.path.join("data", "daily_data.csv"))
    latest_date = df["date"].max()

    # fetch intraday data for that date
    data = get_intraday_hr(ACCESS_TOKEN, latest_date)

    result = []

    for i, entry in enumerate(data):
        result.append({
            "x": i,
            "hr": entry["hr"]
        })

    return result

if __name__ == "__main__":
    app.run(debug=True)