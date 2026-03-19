import joblib
import pandas as pd

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
    mood_model = joblib.load("saved_models/catboost_mood.pkl")
    prod_model = joblib.load("saved_models/random_forest_productivity.pkl")

    # read CSV
    df = pd.read_csv("data/daily_data.csv")

    # latest day
    latest = df.tail(1)

    # remove non-numeric columns
    X = latest.drop(columns=[
        "date",
        "sleep_start_time",
        "wake_time",
        "sleep_midpoint",
        "mood_score",
        "productivity_score"
    ], errors="ignore")

    # -------- PREDICTION --------
    mood = mood_model.predict(X)[0]
    prod = prod_model.predict(X)[0]

    # -------- PRINT (same as your original) --------
    print("\nPrediction for latest day\n")

    print("Mood Score:", round(mood,2))
    print("Mood Meaning:", mood_label(mood))

    print("Productivity Score:", round(prod,2))
    print("Productivity Meaning:", prod_label(prod))

    # 🔥 IMPORTANT: return values for evaluation
    return mood, prod


# -------- RUN DIRECTLY --------
if __name__ == "__main__":
    predict_day()