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
        4:"Slightly low",
        5:"Neutral",
        6:"Okay / decent",
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


# -------- COMMON FEATURE ENGINEERING --------
def prepare_features(df):
    df = df.copy()

    df["sleep_efficiency"] = df["total_sleep"] / df["sleep_hours"].replace(0, 1)
    df["hr_stress_ratio"] = df["avg_hr_day"] / (df["resting_hr"] + 1)

    df["stress_index"] = np.log1p(df["stress_index"])

    df["steps_scaled"] = df["total_steps"] / 10000
    df["stress_sleep_interaction"] = df["stress_index"] * df["sleep_deficit"]

    selected_features = [
        "sleep_efficiency",
        "stress_index",
        "activity_load",
        "hr_stress_ratio",
        "sleep_deficit",
        "steps_scaled",
        "stress_sleep_interaction"
    ]

    return df, selected_features


# -------- RULE ENGINE --------
def apply_rules(row, mood, prod, raw_stress):

    # -------- MOOD --------
    if row['sleep_hours'] < 4:
        mood -= 0.8
    elif row['sleep_hours'] < 6:
        mood -= 0.2

    if raw_stress > 0.18:
        mood -= 0.4
    elif raw_stress > 0.15:
        mood -= 0.2

    if row['sleep_hours'] > 6 and raw_stress < 0.15:
        mood += 0.5

    # -------- PRODUCTIVITY --------
    if row['sleep_hours'] < 4:
        prod -= 0.8
    elif row['sleep_hours'] < 5:
        prod -= 0.4

    if row['total_steps'] < 2000:
        prod -= 0.8
    elif row['total_steps'] < 4000:
        prod -= 0.4
    elif row['total_steps'] > 6000:
        prod += 0.5

    if raw_stress > 0.18:
        prod -= 0.4
    elif raw_stress > 0.15:
        prod -= 0.2

    if row['sleep_hours'] < 6 and raw_stress > 0.18:
        prod -= 0.4

    if mood <= 4:
        prod -= 0.2
    elif mood >= 7:
        prod += 0.2

    # clamp
    mood = max(1, min(10, mood))
    prod = max(1, min(10, prod))

    return round(mood, 2), round(prod, 2)


# -------- MAIN FUNCTION --------
def predict_day():

    mood_model = joblib.load("saved_models/lightgbm_mood.pkl")
    prod_model = joblib.load("saved_models/lightgbm_productivity.pkl")
    scaler = joblib.load("saved_models/scaler.pkl")

    df = pd.read_csv("data/daily_data.csv")

    latest = df.tail(1).copy()
    row = latest.iloc[0]

    raw_stress = row["stress_index"]

    latest, selected_features = prepare_features(latest)

    X = scaler.transform(latest[selected_features])
    X = pd.DataFrame(X, columns=selected_features)

    mood = mood_model.predict(X)[0]
    prod = prod_model.predict(X)[0]

    mood, prod = apply_rules(row, mood, prod, raw_stress)

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
          f"Stress: {round(raw_stress,3)}")

    print("\n--- Activity Suggestions ---")

    if not suggestions:
        print("- Your metrics look balanced. Maintain current routine.")
    else:
        for s in suggestions[:3]:
            print("-", s)

    return mood, prod


# -------- EVALUATION --------
def evaluate_last_days(n=31):

    mood_model = joblib.load("saved_models/lightgbm_mood.pkl")
    prod_model = joblib.load("saved_models/lightgbm_productivity.pkl")
    scaler = joblib.load("saved_models/scaler.pkl")

    df = pd.read_csv("data/daily_data.csv")

    last_days = df.tail(n).copy()

    print("\n===== LAST", n, "DAYS EVALUATION =====\n")

    for i in range(len(last_days)):
        row_df = last_days.iloc[i:i+1].copy()
        row = row_df.iloc[0]

        raw_stress = row["stress_index"]

        row_df, selected_features = prepare_features(row_df)

        X = scaler.transform(row_df[selected_features])
        X = pd.DataFrame(X, columns=selected_features)

        mood_pred = mood_model.predict(X)[0]
        prod_pred = prod_model.predict(X)[0]

        mood_pred, prod_pred = apply_rules(row, mood_pred, prod_pred, raw_stress)

        print(f"\nDate: {row['date']}")
        print(f"Pred Mood: {mood_pred} | Actual: {row['mood_score']}")
        print(f"Pred Prod: {prod_pred} | Actual: {row['productivity_score']}")
        

if __name__ == "__main__":
    predict_day()
    evaluate_last_days(31)
