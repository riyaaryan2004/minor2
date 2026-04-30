import pandas as pd
from datetime import datetime


def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print("Error loading data:", e)
        return None


# -------------------------------
# 1. Trend Analysis
# -------------------------------
def get_trend_insight(df, today_row):
    insights = []

    recent = df.tail(7)

    avg_steps = recent['total_steps'].mean()
    avg_sleep = recent['sleep_hours'].mean()

    if today_row['total_steps'] < 0.7 * avg_steps:
        insights.append("Your activity is lower than your weekly average.")

    if today_row['sleep_hours'] < 0.8 * avg_sleep:
        insights.append("You are sleeping less than your usual pattern.")

    return insights


# -------------------------------
# 2. Consistency (Sleep Stability)
# -------------------------------
def get_consistency_insight(df):
    recent = df.tail(7)

    sleep_std = recent['sleep_hours'].std()

    if sleep_std > 1.5:
        return ["Your sleep schedule is inconsistent. Try maintaining fixed timings."]
    
    return ["Your sleep pattern is fairly consistent."]


# -------------------------------
# 3. Streak Tracking
# -------------------------------
def get_sleep_streak(df):
    streak = 0

    for val in reversed(df['sleep_hours'].tolist()):
        if val >= 7:
            streak += 1
        else:
            break

    if streak >= 3:
        return [f"Great job! You have a {streak}-day good sleep streak 🔥"]
    
    return []


# -------------------------------
# 4. Anomaly Detection
# -------------------------------
def get_anomaly_insight(df, today_row):
    insights = []

    avg_hr = df['avg_hr_day'].mean()

    if today_row['avg_hr_day'] > avg_hr + 10:
        insights.append("Your heart rate is unusually high today. Consider relaxing.")

    if today_row['total_steps'] < 500:
        insights.append("Very low activity detected today.")

    return insights


# -------------------------------
# 5. Behavioral Insight (Correlation)
# -------------------------------
def get_behavior_insight(df):
    insights = []

    if 'mood_score' in df.columns:
        if len(df) >= 5:
            corr = df['total_steps'].corr(df['mood_score'])
            if corr is not None and corr > 0.5:
                insights.append("Higher activity levels seem to improve your mood.")

        if corr is not None and corr > 0.5:
            insights.append("Higher activity levels seem to improve your mood.")

    return insights


# -------------------------------
# 6. Weekly Summary
# -------------------------------
def get_weekly_summary(df):
    recent = df.tail(7)

    avg_sleep = round(recent['sleep_hours'].mean() or 0, 2)
    avg_steps = int(recent['total_steps'].mean() or 0)
    avg_hr = round(recent['avg_hr_day'].mean() or 0, 2)

    summary = (
        f"Weekly Summary:\n"
        f"- Avg Sleep: {avg_sleep} hrs\n"
        f"- Avg Steps: {avg_steps}\n"
        f"- Avg HR: {avg_hr}"
    )

    return [summary]


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def generate_history_insights(file_path):
    df = load_data(file_path)

    if df is None or df.empty:
        return ["No historical data available."]

    # Ensure latest row is today's data
    today_row = df.iloc[-1]

    insights = []

    insights += get_trend_insight(df, today_row)
    insights += get_consistency_insight(df)
    insights += get_sleep_streak(df)
    insights += get_anomaly_insight(df, today_row)
    insights += get_behavior_insight(df)
    insights += get_weekly_summary(df)

    return insights


# -------------------------------
# TEST (optional)
# -------------------------------
if __name__ == "__main__":
    file_path = "../data/daily_data.csv"
    insights = generate_history_insights(file_path)

    print("\n===== HISTORY INSIGHTS =====\n")
    for ins in insights:
        print("-", ins)