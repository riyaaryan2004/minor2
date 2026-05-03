from flask import Blueprint, request, jsonify
import pandas as pd
import os

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

    mood, prod = predict_day(row)

    return {
        "stress": round(row["stress_index"], 3),
        "productivity": round(prod, 2),
        "sleep": round(row["sleep_hours"], 2),
        "mood": round(mood, 2)
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
    mood, prod = predict_day(row)

    # 🔥 STEP 2: Focus Engine
    result = get_task_recommendation(
        row=row,
        mood=mood,
        productivity=prod,
        stress=row["stress_index"],
        tasks=tasks,
        get_activity_suggestions=get_activity_suggestions
    )

    return jsonify(result)