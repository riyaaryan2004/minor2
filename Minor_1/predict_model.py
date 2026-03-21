import joblib
import pandas as pd
import numpy as np   # ✅ added


# load models
mood_model = joblib.load("saved_models/lightgbm_mood.pkl")
prod_model = joblib.load("saved_models/lightgbm_productivity.pkl")


# test scenarios
scenarios = [

{
"name": "Extremely Bad Day",
"day_of_week":2,
"resting_hr":76,
"total_steps":2000,
"total_sleep":180,
"sleep_hours":3,
"deep_ratio":0.18,
"rem_ratio":0.13,
"sleep_deficit":300,
"sleep_start_hour":4,
"wake_hour":7,
"avg_hr_day":95,
"hr_std_day":18,
"hr_deviation":20,
"stress_index":0.20,
"activity_load":0.30,
"is_weekend":0
},

{
"name": "Low Mood Day",
"day_of_week":1,
"resting_hr":74,
"total_steps":3500,
"total_sleep":240,
"sleep_hours":4,
"deep_ratio":0.20,
"rem_ratio":0.15,
"sleep_deficit":240,
"sleep_start_hour":4,
"wake_hour":8,
"avg_hr_day":90,
"hr_std_day":16,
"hr_deviation":18,
"stress_index":0.18,
"activity_load":0.40,
"is_weekend":0
},

{
"name": "Neutral Day",
"day_of_week":3,
"resting_hr":72,
"total_steps":6000,
"total_sleep":360,
"sleep_hours":6,
"deep_ratio":0.23,
"rem_ratio":0.17,
"sleep_deficit":120,
"sleep_start_hour":3,
"wake_hour":9,
"avg_hr_day":85,
"hr_std_day":13,
"hr_deviation":12,
"stress_index":0.16,
"activity_load":0.60,
"is_weekend":0
},

{
"name": "Good Mood Day",
"day_of_week":6,
"resting_hr":70,
"total_steps":7500,
"total_sleep":420,
"sleep_hours":7,
"deep_ratio":0.26,
"rem_ratio":0.19,
"sleep_deficit":60,
"sleep_start_hour":2,
"wake_hour":9,
"avg_hr_day":80,
"hr_std_day":12,
"hr_deviation":10,
"stress_index":0.14,
"activity_load":0.75,
"is_weekend":1
},

{
"name": "Excellent Day",
"day_of_week":0,
"resting_hr":68,
"total_steps":9000,
"total_sleep":480,
"sleep_hours":8,
"deep_ratio":0.28,
"rem_ratio":0.21,
"sleep_deficit":0,
"sleep_start_hour":2,
"wake_hour":10,
"avg_hr_day":78,
"hr_std_day":11,
"hr_deviation":8,
"stress_index":0.13,
"activity_load":0.90,
"is_weekend":1
}

]


# mood mapping
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


# productivity mapping
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


print("\n---- Mood + Productivity Prediction Test ----\n")


for s in scenarios:

    name = s["name"]

    # remove name before prediction
    features = {k:v for k,v in s.items() if k!="name"}

    df = pd.DataFrame([features])

    # -------- FEATURE ENGINEERING (IMPORTANT FIX) --------
    df["sleep_efficiency"] = df["total_sleep"] / df["sleep_hours"].replace(0, 1)
    df["hr_stress_ratio"] = df["avg_hr_day"] / (df["resting_hr"] + 1)

    # same transformation as training
    df["stress_index"] = np.log1p(df["stress_index"])
    # ----------------------------------------------------

    # use SAME features as training
    selected_features = [
        "sleep_efficiency",
        "stress_index",
        "activity_load",
        "hr_stress_ratio",
        "sleep_deficit"
    ]

    X = df[selected_features]

    mood_pred = mood_model.predict(X)[0]
    prod_pred = prod_model.predict(X)[0]

    # -------- RULE-BASED ADJUSTMENT (SAME AS MAIN) --------

    row = df.iloc[0]

    # transformed stress (same as model)
    row_stress = np.log1p(row["stress_index"])

    # Mood adjustments
    if row['sleep_hours'] < 4:
        mood_pred -= 1.0

    elif row['sleep_hours'] < 6:
        mood_pred -= 0.5

    if row_stress > np.log1p(0.18):
        mood_pred -= 0.8

    elif row_stress > np.log1p(0.15):
        mood_pred -= 0.4

    if row['sleep_hours'] > 7 and row_stress < np.log1p(0.14):
        mood_pred += 0.8


    # Productivity adjustments
    if row['total_steps'] < 3000:
        prod_pred -= 0.8

    elif row['total_steps'] < 5000:
        prod_pred -= 0.4

    if row['total_steps'] > 8000:
        prod_pred += 0.6

    if row_stress > np.log1p(0.18):
        prod_pred -= 0.5


    # keep in range
    mood_pred = max(1, min(10, mood_pred))
    prod_pred = max(1, min(10, prod_pred))

    print("Scenario:", name)

    print("Mood Score:", round(mood_pred,2))
    print("Mood Meaning:", mood_label(mood_pred))

    print("Productivity Score:", round(prod_pred,2))
    print("Productivity Meaning:", prod_label(prod_pred))

    print("-----------------------------")