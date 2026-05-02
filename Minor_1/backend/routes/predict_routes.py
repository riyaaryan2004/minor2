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
    result = predict_day(row)    
    print("Requested date:", date)
    print("Available dates:", df["date"].unique())
    return {
    "stress": result["stress"],
    "productivity": round(result["productivity"], 2),
    "sleep": result["sleep"],
    "mood": round(result["mood"], 2),

    "suggestions": result["suggestions"],       
    "day_type": result["day_type"],
    "primary_action": result["primary_action"],
    "root_cause": result["root_cause"],
    "history_insights": result["history_insights"],
    "daily_goal": result["daily_goal"]
}
