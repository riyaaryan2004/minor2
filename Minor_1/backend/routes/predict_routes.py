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

    # ✅ ALWAYS treat as dict
    prediction = predict_day(row)

    return jsonify({
        "stress": prediction.get("stress"),
        "productivity": round(prediction.get("productivity", 0), 2),
        "sleep": prediction.get("sleep"),
        "steps": int(row["total_steps"]) if pd.notna(row.get("total_steps")) else None,
        "mood": round(prediction.get("mood", 0), 2),
        "insight": prediction.get("insight"),

        "suggestions": prediction.get("suggestions"),
        "day_type": prediction.get("day_type"),
        "primary_action": prediction.get("primary_action"),
        "root_cause": prediction.get("root_cause"),
        "history_insights": prediction.get("history_insights"),
        "daily_goal": prediction.get("daily_goal")
    })


# -----------------------------------
# 🚀 NEW FOCUS ENGINE ROUTE
# -----------------------------------
@predict_bp.route("/focus", methods=["POST"])
def focus():

    data = request.json or {}
    tasks = data.get("tasks", [])
    date = _clean_date(data.get("date"))

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
    insight = prediction.get("insight", "")

    # 🔥 STEP 2: Recommendation (keep your existing logic)
    result = get_task_recommendation(
        row=row,
        mood=mood,
        productivity=prod,
        stress=row["stress_index"],
        tasks=tasks,
        get_activity_suggestions=get_activity_suggestions
    )

    if not result or "task" not in result:
        return {"error": "Could not generate recommendation"}, 500

    # 🔥 STEP 3: 🔥 NEW → TASK RANKING LOGIC
    ranked_tasks = []

    for t in tasks:
        base = prod

        # difficulty
        if t["type"] == "deep":
            base -= 15
        elif t["type"] == "light":
            base += 10

        # duration
        if t["duration"] > 90:
            base -= 10

        # mood
        if mood == "focused":
            base += 10
        elif mood == "tired":
            base -= 15

        # priority boost
        base += t["priority"] * 5

        score = max(0, min(100, int(base)))

        ranked_tasks.append({
            "task": t["task"],
            "score": score,
            "priority": t["priority"],
            "duration": t["duration"],
            "type": t["type"]
        })

    # 🔥 sort tasks (best first)
    ranked_tasks = sorted(ranked_tasks, key=lambda x: x["score"], reverse=True)

    # 🔥 STEP 4: Best task (top ranked)
    best_task_data = ranked_tasks[0]
    best_task_name = best_task_data["task"]

    # 🔍 find full task object
    task = next((t for t in tasks if t["task"] == best_task_name), None)

    if task:
        success_prob = best_task_data["score"]

        # burnout logic
        risk = 0

        if task["type"] == "deep":
            risk += 30

        if task["duration"] > 90:
            risk += 20

        if prod < 40:
            risk += 30

        if row["stress_index"] > 70:
            risk += 20

        if risk > 60:
            burnout = "High"
        elif risk > 30:
            burnout = "Medium"
        else:
            burnout = "Low"

        result["success_probability"] = success_prob
        result["burnout_risk"] = burnout
        result["confidence"] = success_prob
    else:
        result["success_probability"] = None
        result["burnout_risk"] = None
        result["confidence"] = None

    # 🔥 STEP 5: Inject new features
    result["task_order"] = ranked_tasks   # 👈 IMPORTANT
    result["insight"] = insight

    return jsonify(result)
