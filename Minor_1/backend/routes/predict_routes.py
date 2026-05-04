from contextlib import redirect_stdout
from flask import Blueprint, request, jsonify
import io
import os
import pandas as pd

from ml.features.predict_day import predict_day
from ml.features.routine_engine import get_task_recommendation
from ml.features.activity_suggestion import get_activity_suggestions
from backend.config import DATA_DIR


predict_bp = Blueprint("predict", __name__)


def _clean_date(date):
    if not date or date in {"undefined", "null"}:
        return None
    return str(date).strip()

# -----------------------------------
# 📊 EXISTING PREDICT ROUTE
# -----------------------------------
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

    with redirect_stdout(io.StringIO()):
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


# -----------------------------------
# 🚀 NEW FOCUS ENGINE ROUTE
# -----------------------------------
@predict_bp.route("/focus", methods=["POST"])
def focus():

    data = request.json or {}
    tasks = data.get("tasks", [])
    date = _clean_date(data.get("date"))

    # ❗ Safety check
    if not tasks:
        return {"error": "No tasks provided"}, 400

    df = pd.read_csv(os.path.join(DATA_DIR, "daily_data.csv"))
    df["date"] = df["date"].astype(str).str.strip()

    if date:
        df = df[df["date"] == date]

    if df.empty:
        return {"error": "No data available"}, 404

    row = df.tail(1).iloc[0]

    # 🔥 STEP 1: Prediction
    prediction = predict_day(row)

    mood = prediction["mood"]
    prod = prediction["productivity"]

    result = get_task_recommendation(
        row=row,
        mood=mood,
        productivity=prod,
        stress=row["stress_index"],
        tasks=tasks,
        get_activity_suggestions=get_activity_suggestions
    )

    return jsonify(result)
