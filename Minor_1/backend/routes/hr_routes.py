from flask import Blueprint, request
import pandas as pd
import os
from backend.config import DATA_DIR
from backend.services.token_service import get_token
from ml.features.hr_live import get_intraday_hr
hr_bp = Blueprint("hr", __name__)

@hr_bp.route("/hr-data")
def hr_data():
    date = request.args.get("date")

    df = pd.read_csv(os.path.join(DATA_DIR, "hourly_data.csv"))

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
    date = request.args.get("date")
    token = get_token()

    if not token:
        return {"error": "Missing token"}, 400

    if not date:
        import pandas as pd
        df = pd.read_csv(os.path.join(DATA_DIR, "daily_data.csv"))
        date = df["date"].max()

    data = get_intraday_hr(token, date)

    return [{"x": i, "hr": d["hr"]} for i, d in enumerate(data)]