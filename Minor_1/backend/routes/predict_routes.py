from flask import Blueprint, request
import pandas as pd
import os
from ml.features.predict_day import predict_day
from backend.config import DATA_DIR


predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict")
def predict():
    date = request.args.get("date")

    df = pd.read_csv(os.path.join(DATA_DIR, "daily_data.csv"))
    if date:
        df = df[df["date"] == date]

    if df.empty:
        return {"error": "No data for selected date"}, 404

    row = df.tail(1).iloc[0]

    # ✅ pass row to ML (important)
    result = predict_day(row)    
    print("Requested date:", date)
    print("Available dates:", df["date"].unique())
    return result