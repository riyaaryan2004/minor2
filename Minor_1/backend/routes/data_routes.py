from flask import Blueprint, request
import pandas as pd
import os
from datetime import datetime
from backend.config import DATA_DIR
from backend.services.token_service import get_token
from ml.features.activity_suggestion import get_activity_suggestions
from ml.features.alerts import get_alerts
from ml.features.movie_recommendor import recommend_movies
from ml.features.predict_day import predict_day
from ml.repair_day import repair_day


data_bp = Blueprint("data", __name__)

def _clean_date(date):
    if not date or date in {"undefined", "null"}:
        return None

    return date

def _get_daily_row(date=None):
    date = _clean_date(date)
    df = pd.read_csv(os.path.join(DATA_DIR, "daily_data.csv"))

    if date:
        df = df[df["date"] == date]

    if df.empty:
        return None

    return df.tail(1).iloc[0]

@data_bp.route("/rate")
def rate():
    mood = request.args.get("mood")
    productivity = request.args.get("productivity")
    date = request.args.get("date")

    if not mood or not productivity:
        return {"error": "Provide mood and productivity"}, 400

    if not date:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

    import pandas as pd
    df = pd.read_csv(os.path.join(DATA_DIR, "daily_data.csv"))

    if date not in df["date"].values:
        return {"error": "Date not found"}, 404

    df.loc[df["date"] == date, "mood_score"] = mood
    df.loc[df["date"] == date, "productivity_score"] = productivity

    df.to_csv(os.path.join(DATA_DIR, "daily_data.csv"), index=False)

    return {"status": "Saved"}

@data_bp.route("/sync-day", methods=["GET","POST"])
def sync_day():
    date = _clean_date(request.args.get("date"))
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    token = get_token()
    if not token:
        return {"error": "Fitbit token missing. Login again first."}, 400

    try:
        result = repair_day(date, token)
    except (RuntimeError, ValueError) as exc:
        return {"error": str(exc)}, 502

    return {"status": "updated", **result}

@data_bp.route("/activity")
def activity():
    date = _clean_date(request.args.get("date"))
    row = _get_daily_row(date)

    if row is None:
        return {"error": "No data for selected date"}, 404

    mood, productivity = predict_day(row)
    suggestions = get_activity_suggestions(
        row,
        mood,
        productivity,
        row["stress_index"],
    )

    return {"suggestions": suggestions}

@data_bp.route("/alerts")
def alerts():
    date = _clean_date(request.args.get("date"))
    return {"alerts": get_alerts(date)}

@data_bp.route("/movies")
def movies():
    date = _clean_date(request.args.get("date"))
    row = _get_daily_row(date)

    if row is None:
        df = pd.read_csv(os.path.join(DATA_DIR, "daily_data.csv"))
        
        if df.empty:
            return {"movies": []}
        
        # fallback to latest available data
        row = df.tail(1).iloc[0]

    try:
        import io
        from contextlib import redirect_stdout

        with redirect_stdout(io.StringIO()):
            movies_list = recommend_movies(row)

        return {"movies": movies_list}

    except Exception as e:
        print("Movie error:", e)
        return {"movies": []}