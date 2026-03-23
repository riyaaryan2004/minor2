import pandas as pd

# =========================
# 1. LOAD DATA
# =========================

def load_concat(f1, f2):
    return pd.concat([pd.read_csv(f1), pd.read_csv(f2)], ignore_index=True)

daily = load_concat("data/dailyActivity_merged.csv",
                    "data/dailyActivity_merged (2).csv")

hsteps = load_concat("data/hourlySteps_merged.csv",
                     "data/hourlySteps_merged (2).csv")

hint = load_concat("data/hourlyIntensities_merged.csv",
                   "data/hourlyIntensities_merged (2).csv")

hr = load_concat("data/heartrate_seconds_merged.csv",
                 "data/heartrate_seconds_merged (2).csv")

msleep = load_concat("data/minuteSleep_merged.csv",
                     "data/minuteSleep_merged (2).csv")

# =========================
# 2. DATE STANDARDIZATION
# =========================

daily["date"] = pd.to_datetime(daily["ActivityDate"]).dt.date

hsteps["date"] = pd.to_datetime(hsteps["ActivityHour"]).dt.date
hint["date"] = pd.to_datetime(hint["ActivityHour"]).dt.date

hr["Time"] = pd.to_datetime(hr["Time"], errors="coerce")
hr = hr.dropna(subset=["Time"])
hr["date"] = hr["Time"].dt.date

msleep["dateTime"] = pd.to_datetime(msleep["date"])

# =========================
# 3. DAILY FEATURES
# =========================

daily_main = daily[[
    "Id","date","TotalSteps",
    "VeryActiveMinutes","FairlyActiveMinutes",
    "LightlyActiveMinutes"
]]

steps_daily = hsteps.groupby(["Id","date"])["StepTotal"].sum().reset_index()
intensity_daily = hint.groupby(["Id","date"])["TotalIntensity"].sum().reset_index()

# =========================
# 4. HEART RATE
# =========================

hr_daily = hr.groupby(["Id","date"])["Value"].agg(
    avg_hr_day="mean",
    hr_std_day="std",
    min_hr="min",
    max_hr="max"
).reset_index()

hr_daily["resting_hr"] = hr_daily["min_hr"]
hr_daily["hr_deviation"] = hr_daily["avg_hr_day"] - hr_daily["resting_hr"]

# =========================
# 5. SLEEP (CORRECT LOGIC)
# =========================

msleep = msleep.sort_values(["Id","dateTime"])

msleep["prev"] = msleep.groupby("Id")["value"].shift()
msleep["new_session"] = (msleep["value"] == 1) & (msleep["prev"] != 1)
msleep["session_id"] = msleep.groupby("Id")["new_session"].cumsum()

sleep_sessions = msleep[msleep["value"] == 1]

sessions = sleep_sessions.groupby(["Id","session_id"]).agg(
    sleep_start_time=("dateTime","min"),
    wake_time=("dateTime","max")
).reset_index()

# duration per session
sessions["duration"] = (
    sessions["wake_time"] - sessions["sleep_start_time"]
).dt.total_seconds()

sessions["date"] = sessions["sleep_start_time"].dt.date

# ✅ pick longest session per day
sleep_timing = sessions.loc[
    sessions.groupby(["Id","date"])["duration"].idxmax()
].reset_index(drop=True)

# duration features
sleep_timing["total_sleep"] = sleep_timing["duration"] / 60
sleep_timing["sleep_hours"] = sleep_timing["total_sleep"] / 60

# midpoint
sleep_timing["sleep_midpoint"] = (
    sleep_timing["sleep_start_time"] +
    (sleep_timing["wake_time"] - sleep_timing["sleep_start_time"]) / 2
)

sleep_timing["sleep_start_hour"] = sleep_timing["sleep_start_time"].dt.hour
sleep_timing["wake_hour"] = sleep_timing["wake_time"].dt.hour

# =========================
# 6. MERGE
# =========================

df = daily_main.copy()

df = df.merge(steps_daily, on=["Id","date"], how="left")
df = df.merge(intensity_daily, on=["Id","date"], how="left")
df = df.merge(hr_daily, on=["Id","date"], how="left")
df = df.merge(sleep_timing, on=["Id","date"], how="left")

# remove duplicates safely
df = df.sort_values(["Id","date","total_sleep"], ascending=[True,True,False])
df = df.drop_duplicates(["Id","date"])

# =========================
# 7. FEATURE ENGINEERING
# =========================

df["day_of_week"] = pd.to_datetime(df["date"]).dt.dayofweek
df["is_weekend"] = df["day_of_week"].isin([5,6]).astype(int)

df["activity_load"] = (
    df["VeryActiveMinutes"]*3 +
    df["FairlyActiveMinutes"]*2 +
    df["LightlyActiveMinutes"]
)

df["sleep_deficit"] = 8 - df["sleep_hours"]

df["resting_hr"] = df["resting_hr"].fillna(df["avg_hr_day"] - df["hr_std_day"])
df["stress_index"] = df["hr_std_day"] / (df["resting_hr"] + 1)

# =========================
# 8. FORMAT OUTPUT
# =========================

final_df = pd.DataFrame()

final_df["date"] = pd.to_datetime(df["date"])

final_df["day_of_week"] = df["day_of_week"]
final_df["resting_hr"] = df["resting_hr"].round(0)

final_df["total_steps"] = df["TotalSteps"]

final_df["total_sleep"] = df["total_sleep"].round(0)
final_df["sleep_hours"] = df["sleep_hours"].round(2)

final_df["deep_ratio"] = 0.25
final_df["rem_ratio"] = 0.19

final_df["sleep_deficit"] = (df["sleep_deficit"] * 60).round(0)

final_df["sleep_start_time"] = df["sleep_start_time"]
final_df["wake_time"] = df["wake_time"]

# midpoint formatted HH:MM:SS
final_df["sleep_midpoint"] = df["sleep_midpoint"].dt.strftime("%H:%M:%S")

final_df["sleep_start_hour"] = df["sleep_start_hour"]
final_df["wake_hour"] = df["wake_hour"]

final_df["avg_hr_day"] = df["avg_hr_day"].round(2)
final_df["hr_std_day"] = df["hr_std_day"].round(2)
final_df["hr_deviation"] = df["hr_deviation"].round(2)

final_df["stress_index"] = df["stress_index"].round(4)

final_df["activity_load"] = (df["activity_load"]/1000).round(2)

final_df["is_weekend"] = df["is_weekend"]

final_df["mood_score"] = pd.NA
final_df["productivity_score"] = pd.NA

# =========================
# 9. SAVE
# =========================

final_df = final_df.sort_values("date")

final_df.to_csv("data/final_dataset_clean.csv", index=False)

print("✅ FINAL DATASET READY")
print(final_df.head())