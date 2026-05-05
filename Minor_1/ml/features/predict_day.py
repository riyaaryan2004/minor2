import joblib
import pandas as pd
import numpy as np 

from ml.features.activity_suggestion import get_activity_suggestions
from ml.features.history_insights import generate_history_insights
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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

# -------- NEW: DAY TYPE --------
def get_day_type(row, mood, prod, stress):
    if row["sleep_hours"] < 5 and stress > 0.15:
        return "Recovery Needed"
    elif mood >= 7 and prod >= 7:
        return "High Performance Day"
    elif mood >= 5 and prod >= 5:
        return "Balanced Day"
    else:
        return "Low Energy Day"
    
# -------- NEW: ROOT CAUSE --------
def get_root_cause(row, stress):
    causes = []
    if row["sleep_hours"] < 5:
        causes.append("low sleep")
    if stress > 0.18:
        causes.append("high stress")
    if row["total_steps"] < 3000:
        causes.append("low activity")
    return ", ".join(causes) if causes else "no major issues"

# -------- NEW: PRIMARY ACTION --------
def get_primary_action(row, stress):
    sleep = round(row["sleep_hours"], 1)
    steps = int(row["total_steps"])

    if stress > 0.18:
        return (
            f"Stress is elevated ({round(stress, 3)}), so keep today focused on lower-pressure work. "
            "Handle one important task at a time, take a 5-10 minute reset break, and avoid stacking intense tasks back to back."
        )
    if row["sleep_hours"] < 5:
        return (
            f"Sleep is low ({sleep} hrs), so use today as a recovery-focused day. "
            "Prioritize essential work first, keep non-urgent tasks lighter, and aim for an earlier wind-down tonight."
        )
    if row["total_steps"] < 3000:
        return (
            f"Activity is low so far ({steps} steps). Add a realistic movement target with a short 10-15 minute walk "
            "or two small walking breaks to improve energy without overdoing it."
        )
    return (
        f"Your core signals look stable today: {sleep} hrs sleep, {steps} steps, and stress at {round(stress, 3)}. "
        "Maintain the routine, protect breaks, and avoid pushing intensity unnecessarily."
    )


# -------- NEW: DAILY GOAL --------
def get_daily_goal(df, row):
    avg_steps = df['total_steps'].mean()
    target = int(avg_steps + 500)
    current_steps = int(row['total_steps'])

    if row['total_steps'] >= avg_steps:
        return (
            f"Maintain at least {int(avg_steps)} steps today. You are currently at {current_steps}, "
            "so focus on consistency: one light walk later is enough to stay near your weekly rhythm."
        )
    else:
        remaining = max(0, target - current_steps)
        return (
            f"Reach about {target} steps today. You are currently at {current_steps}, "
            f"so add roughly {remaining} more steps through 2-3 short walks instead of one long push."
        )
    
    
# -------- COMMON FEATURE ENGINEERING --------
def prepare_features(df):
    df = df.copy()

    df["sleep_efficiency"] = df["total_sleep"] / df["sleep_hours"].replace(0, 1)
    df["hr_stress_ratio"] = df["avg_hr_day"] / (df["resting_hr"] + 1)

    df["stress_index_log"] = np.log1p(df["stress_index"])

    df["steps_scaled"] = df["total_steps"] / 10000
    df["stress_sleep_interaction"] = df["stress_index_log"] * df["sleep_deficit"]

    selected_features = [
        "sleep_efficiency",
        "stress_index_log",   
        "activity_load",
        "hr_stress_ratio",
        "sleep_deficit",
        "steps_scaled",
        "stress_sleep_interaction"
    ]

    return df, selected_features

# -------- RULE ENGINE --------
def apply_rules(row, mood, prod, raw_stress):

    # -------- EXTREME SLEEP --------
    if row['sleep_hours'] < 3:
        mood -= 0.5
        prod -= 0.5
    elif row['sleep_hours'] > 8:
        mood += 0.2   # reward good sleep

    # -------- EXTREME STRESS --------
    if raw_stress > 0.20:
        mood -= 0.3
        prod -= 0.3

    # -------- ACTIVITY BOOST --------
    if row['total_steps'] > 7000:
        prod += 0.3

    # -------- VERY LOW ACTIVITY --------
    if row['total_steps'] < 1500:
        prod -= 0.4
        
    # -------- EXTREME INACTIVITY --------
    if row['total_steps'] < 100:
        mood -= 0.7
        prod -= 1.0

    # -------- CLAMP --------
    mood = max(1, min(10, mood))
    prod = max(1, min(10, prod))

    return round(mood, 2), round(prod, 2)

def generate_summary(row, mood, prod, raw_stress):
    sleep = row["sleep_hours"]
    stress = raw_stress
    steps = row["total_steps"]

    if sleep >= 6 and steps >= 5000 and stress < 0.17:
        return "You're in a stable and balanced state today."

    if stress > 0.18:
        return "Stress is the main factor affecting your day."

    if sleep < 5:
        return "Low sleep is slightly impacting your performance."

    if steps < 4000:
        return "Low activity might be reducing your energy levels."

    return "Overall performance is moderate with no major concerns."

# -------- MAIN FUNCTION --------
def predict_day(row):

    mood_model = joblib.load(os.path.join(BASE_DIR, "saved_models", "random_forest_mood.pkl"))
    prod_model = joblib.load(os.path.join(BASE_DIR, "saved_models", "random_forest_productivity.pkl"))
    scaler = joblib.load(os.path.join(BASE_DIR, "saved_models", "scaler.pkl"))

    df = pd.DataFrame([row])   # ✅ use selected date row
    latest = df.copy()
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

    print(get_day_type(row, mood, prod, raw_stress))
    print("\nRoot Cause:", get_root_cause(row, raw_stress))

    print("\nKey Metrics:")
    print(f"Sleep: {round(row['sleep_hours'],1)} hrs | "
          f"Steps: {int(row['total_steps'])} | "
          f"Stress: {round(raw_stress,3)}")

    print("\n🎯 Primary Action:")
    print("-", get_primary_action(row, raw_stress))

    suggestions = get_activity_suggestions(row, mood, prod, raw_stress)

    print("\n💡 Supporting Actions:")
    if not suggestions:
        print("- Maintain your current routine.")
    else:
        for s in suggestions[:2]:
            print("-", s)

    print("\n📊 History Insight:")
    history_insights = generate_history_insights(
        os.path.join(BASE_DIR, "data", "daily_data.csv")
    )
    if history_insights:
        for ins in history_insights[:2]:
            print("-", ins)

    df_full = pd.read_csv(os.path.join(BASE_DIR, "data", "daily_data.csv"))
    print("\n🎯 Daily Goal:")
    print("-", get_daily_goal(df_full, row))

    print("\nInsight:", generate_summary(row, mood, prod, raw_stress))

    return {
        "mood": mood,
        "productivity": prod,
        "day_type": get_day_type(row, mood, prod, raw_stress),
        "root_cause": get_root_cause(row, raw_stress),
        "primary_action": get_primary_action(row, raw_stress),
        "suggestions": suggestions,
        "history_insights": generate_history_insights(
            os.path.join(BASE_DIR, "data", "daily_data.csv")
        ),
        "daily_goal": get_daily_goal(
            pd.read_csv(os.path.join(BASE_DIR, "data", "daily_data.csv")),
            row
        ),
        "sleep": round(row["sleep_hours"], 2),
        "stress": round(row["stress_index"], 3)
    }
        

if __name__ == "__main__":
    import pandas as pd
    import os

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "daily_data.csv"))

    # Example: choose mode
    date_input = None  # or "2026-04-30"

    if date_input:
        row = df[df["date"] == date_input].iloc[0]
    else:
        row = df.tail(1).iloc[0]   # default latest

    predict_day(row)
    #evaluate_last_days(7)
