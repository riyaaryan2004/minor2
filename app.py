from flask import Flask, redirect, request
import requests
import base64
import csv
import os
from datetime import datetime

app = Flask(__name__)

CLIENT_ID = "23TXMK"
CLIENT_SECRET = "b19bed40782c38915f7a78687262612b"
REDIRECT_URI = "http://localhost:5000/callback"


@app.route("/")
def home():
    return "Server Running"


@app.route("/login")
def login():
    auth_url = (
        "https://www.fitbit.com/oauth2/authorize"
        f"?response_type=code&client_id={CLIENT_ID}"
        "&scope=heartrate activity sleep"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)


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
        return {
            "error": "Token exchange failed",
            "fitbit_response": response.json()
        }, 400

    token_data = response.json()
    access_token = token_data["access_token"]

    return redirect(f"/heartrate?token={access_token}")


@app.route("/heartrate")
def heartrate():
    access_token = request.args.get("token")

    if not access_token:
        return {"error": "Missing access token"}, 400

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # ---------------- HEART DATA ----------------
    heart_url = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d.json"
    heart_response = requests.get(heart_url, headers=headers)
    heart_data = heart_response.json()

    # ---------------- STEPS DATA ----------------
    steps_url = "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json"
    steps_response = requests.get(steps_url, headers=headers)
    steps_data = steps_response.json()

    # Extract heart zones
    zones = heart_data["activities-heart"][0]["value"]["heartRateZones"]
    resting_hr = heart_data["activities-heart"][0]["value"].get("restingHeartRate", 70)

    out_range = zones[0]["minutes"]
    fat_burn = zones[1]["minutes"]
    cardio = zones[2]["minutes"]
    peak = zones[3]["minutes"]

    # Extract steps
    steps = int(steps_data["activities-steps"][0]["value"])

    # ---------------- FEATURE ENGINEERING ----------------

    total_minutes = out_range + fat_burn + cardio + peak

    intensity_ratio = (
        (fat_burn + cardio + peak) / total_minutes
        if total_minutes else 0
    )

    # Custom energy-style score (0–100 approx)
    activity_score = (
        (fat_burn * 1.5) +
        (cardio * 2) +
        (peak * 3) +
        (steps / 1000)
    )

    activity_score = min(activity_score, 100)

    step_intensity = steps / 10000  # normalized

    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday()

    # ---------------- SAVE STRUCTURED CSV ----------------

    os.makedirs("data", exist_ok=True)
    csv_file_path = "data/structured_fitbit_data.csv"
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "hour",
                "day_of_week",
                "out_of_range",
                "fat_burn",
                "cardio",
                "peak",
                "resting_hr",
                "steps",
                "intensity_ratio",
                "activity_score",
                "step_intensity"
            ])

        writer.writerow([
            now,
            hour,
            day_of_week,
            out_range,
            fat_burn,
            cardio,
            peak,
            resting_hr,
            steps,
            intensity_ratio,
            activity_score,
            step_intensity
        ])

    # ---------------- RETURN CLEAN FEATURE OUTPUT ----------------

    return {
        "hour": hour,
        "day_of_week": day_of_week,
        "resting_hr": resting_hr,
        "steps": steps,
        "intensity_ratio": intensity_ratio,
        "activity_score": activity_score,
        "step_intensity": step_intensity
    }

if __name__ == "__main__":
    app.run(debug=True)