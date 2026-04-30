from flask import Blueprint, request
import pandas as pd
import os
from ml.features.predict_day import predict_day
from backend.config import DATA_DIR


predict_bp = Blueprint("predict", __name__)

def _clean_date(date):
    if not date or date in {"undefined", "null"}:
        return None

    return str(date).strip()

@predict_bp.route("/predict")
def predict():
    date = _clean_date(request.args.get("date"))

    df = pd.read_csv(os.path.join(DATA_DIR, "daily_data.csv"))
    df["date"] = df["date"].astype(str).str.strip()

    if date:
        df = df[df["date"] == date]

    if df.empty:
        return {"error": "No data for selected date"}, 404

    row = df.tail(1).iloc[0]

    # ✅ pass row to ML (important)
    mood, prod = predict_day(row)
    print("Requested date:", date)
    print("Available dates:", df["date"].unique())
    return {
        "stress": round(row["stress_index"], 3),
        "productivity": round(prod, 2),
        "sleep": round(row["sleep_hours"], 2),
        "mood": round(mood, 2)
    }
