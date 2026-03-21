import joblib
import pandas as pd
import numpy as np 

from activity_suggestion import get_activity_suggestions


# -------- MOOD TAGS --------
def mood_label(score):

    score = round(score)

    mapping = {
        1:"Extremely bad mood",
        2:"Very low mood",
        3:"Low mood",
        4:"Mildly negative",
        5:"Neutral",
        6:"Slightly positive",
        7:"Good",
        8:"Very good",
        9:"Great mood",
        10:"Excellent"
    }

    return mapping.get(score,"Unknown")


# -------- PRODUCTIVITY TAGS --------
def prod_label(score):

    score = round(score)

    mapping = {
        1: "Extremely low productivity",
        2: "Very low productivity",
        3: "Low productivity",
        4: "Below average",
        5: "Average",
        6: "Above average",
        7: "Good productivity",
        8: "Very productive",
        9: "Highly productive",
        10: "Extremely productive"
    }

    return mapping.get(score,"Unknown")


# -------- MAIN FUNCTION --------
def predict_day():

    # load models
    mood_model = joblib.load("saved_models/lightgbm_mood.pkl")
    prod_model = joblib.load("saved_models/lightgbm_productivity.pkl")

    # read CSV
    df = pd.read_csv("data/daily_data.csv")

    # latest day
    latest = df.tail(1).copy()   # ✅ safe copy

    # extract row for suggestions
    row = latest.iloc[0]

    # ---------------- FEATURE ENGINEERING (IMPORTANT FIX) ----------------
    latest["sleep_efficiency"] = latest["total_sleep"] / latest["sleep_hours"].replace(0, 1)
    latest["hr_stress_ratio"] = latest["avg_hr_day"] / (latest["resting_hr"] + 1)

    # same log transform as training
    latest["stress_index"] = np.log1p(latest["stress_index"])

    # ✅ create transformed stress for rules (FIX)
    row_stress = np.log1p(row["stress_index"])
    # --------------------------------------------------------------------

    # ONLY use same features as training
    selected_features = [
        "sleep_efficiency",
        "stress_index",
        "activity_load",
        "hr_stress_ratio",
        "sleep_deficit"
    ]

    X = latest[selected_features]

    # -------- PREDICTION --------
    mood = mood_model.predict(X)[0]
    prod = prod_model.predict(X)[0]
    
   # ---------------- RULE-BASED ADJUSTMENT (IMPROVED) ----------------

    # Mood adjustments
    if row['sleep_hours'] < 4:
        mood -= 1.0

    elif row['sleep_hours'] < 6:
        mood -= 0.5

    if row_stress > np.log1p(0.18):
        mood -= 0.8

    elif row_stress > np.log1p(0.15):
        mood -= 0.4

    if row['sleep_hours'] > 7 and row_stress < np.log1p(0.14):
        mood += 0.8


    # Productivity adjustments
    if row['total_steps'] < 3000:
        prod -= 0.8

    elif row['total_steps'] < 5000:
        prod -= 0.4

    if row['total_steps'] > 8000:
        prod += 0.6

    if row_stress > np.log1p(0.18):
        prod -= 0.5

    # ---------------------------------------------------------------


    # keep values in valid range
    mood = max(1, min(10, mood))
    prod = max(1, min(10, prod))
    
    mood = round(mood, 2)
    prod = round(prod, 2)

    print("\n" + "="*40)
    print("\n===== DAILY HEALTH INSIGHT =====\n")

    print("Mood Score:", mood)
    print("Mood Meaning:", mood_label(mood))

    print("Productivity Score:", prod)
    print("Productivity Meaning:", prod_label(prod))

    suggestions = get_activity_suggestions(row, mood, prod)

    print("\nKey Metrics:")
    print(f"Sleep: {round(row['sleep_hours'],1)} hrs | "
        f"Steps: {int(row['total_steps'])} | "
        f"Stress: {round(row['stress_index'],3)}")

    print("\n--- Activity Suggestions ---")

    if not suggestions:
        print("- Your metrics look balanced. Maintain current routine.")
    else:
        for s in suggestions[:3]:
            print("-", s)

    return mood, prod


if __name__ == "__main__":
    predict_day()