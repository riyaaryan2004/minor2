import joblib
import pandas as pd

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
        1:"No work done",
        2:"Very low productivity",
        3:"Low productivity",
        4:"Slightly low",
        5:"Average",
        6:"Decent productivity",
        7:"Good productivity",
        8:"Very productive",
        9:"Highly productive",
        10:"Extremely productive"
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
    latest = df.tail(1)

    # extract row for suggestions
    row = latest.iloc[0]

    # ONLY use same features as training
    selected_features = [
        "hr_std_day",
        "day_of_week",
        "total_steps",
        "avg_hr_day",
        "activity_load",
        "stress_index"
    ]

    X = latest[selected_features]

    # -------- PREDICTION --------
    mood = mood_model.predict(X)[0]
    prod = prod_model.predict(X)[0]
    
    # productivity strongly depends on activity + stress
    if row['total_steps'] < 4000:
        prod -= 0.3

    if row['stress_index'] > 0.15:
        prod -= 0.2

    # slight mood adjustment
    if row['stress_index'] > 0.17:
        mood -= 0.3


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