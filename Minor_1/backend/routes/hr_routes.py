from flask import Blueprint, request
import pandas as pd
import os
from datetime import datetime
from backend.config import DATA_DIR
from backend.services.token_service import get_token
from ml.features.hr_live import get_intraday_hr, get_intraday_hr_response
hr_bp = Blueprint("hr", __name__)

def _clean_date(date):
    if not date or date in {"undefined", "null"}:
        return None

    return str(date).strip()

@hr_bp.route("/hr-data")
def hr_data():
    date = _clean_date(request.args.get("date"))

    df = pd.read_csv(os.path.join(DATA_DIR, "hourly_data.csv"))
    df["date"] = df["date"].astype(str).str.strip()

    if date:
        df = df[df["date"] == date]
    else:
        df = df[df["date"] == df["date"].max()]

    df = df.dropna(subset=["avg_hr"])

    return [
        {"hour": int(r["hour"]), "hr": round(r["avg_hr"], 1)}
        for _, r in df.iterrows()
    ]


@hr_bp.route("/hr-minute")
def hr_minute():
    date = _clean_date(request.args.get("date"))
    token = get_token()

    if not token:
        return {"error": "Missing token"}, 400

    if not date:
        import pandas as pd
        df = pd.read_csv(os.path.join(DATA_DIR, "daily_data.csv"))
        date = df["date"].max()

    data = get_intraday_hr(token, date)

    return [{"x": i, "hr": d["hr"]} for i, d in enumerate(data)]


@hr_bp.route("/hr-latest")
def hr_latest():
    date = _clean_date(request.args.get("date"))
    token = get_token()
    checked_at = datetime.now().strftime("%H:%M:%S")

    if not token:
        return {"error": "Missing token"}, 400

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    live_error = None

    try:
        live_response = get_intraday_hr_response(token, date)
        data = live_response["data"]
        if live_response["statusCode"] != 200:
            errors = live_response.get("errors") or []
            live_error = errors[0].get("errorType", "fitbit_api_error") if errors else "fitbit_api_error"
        elif not data:
            live_error = "no_live_points"
    except Exception as exc:
        data = []
        live_error = "fitbit_connection_error"

    if not data:
        hourly = pd.read_csv(os.path.join(DATA_DIR, "hourly_data.csv"))
        hourly["date"] = hourly["date"].astype(str).str.strip()
        hourly = hourly[(hourly["date"] == date) & hourly["avg_hr"].notna()]

        if hourly.empty:
            return {"error": "No live heart-rate data available", "date": date}, 404

        latest_hour = hourly.tail(1).iloc[0]
        return {
            "date": date,
            "time": f"{int(latest_hour['hour']):02d}:00",
            "hr": round(float(latest_hour["avg_hr"]), 1),
            "points": len(hourly),
            "source": "saved-hourly",
            "liveError": live_error,
            "checkedAt": checked_at,
        }

    latest = data[-1]
    return {
        "date": date,
        "time": latest["time"],
        "hr": latest["hr"],
        "points": len(data),
        "source": "fitbit-live",
        "checkedAt": checked_at,
    }
