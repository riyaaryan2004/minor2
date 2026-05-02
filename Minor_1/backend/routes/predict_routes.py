from contextlib import redirect_stdout
from flask import Blueprint, request
import io
import os
import pandas as pd

from backend.config import DATA_DIR
from ml.features.predict_day import predict_day


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

    # predict_day prints a console report; keep this endpoint JSON-only and
    # avoid Windows console encoding crashes from decorative characters.
    with redirect_stdout(io.StringIO()):
        result = predict_day(row)

    print("Requested date:", date)
    print("Available dates:", df["date"].unique())

    return {
        "stress": result["stress"],
        "productivity": result["productivity"],
        "sleep": result["sleep"],
        "mood": result["mood"],
        "day_type": result.get("day_type"),
        "root_cause": result.get("root_cause"),
        "primary_action": result.get("primary_action"),
        "daily_goal": result.get("daily_goal"),
    }
