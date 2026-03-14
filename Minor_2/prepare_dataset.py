import pandas as pd
import os
# print(os.listdir())

daily1 = pd.read_csv("data/dailyActivity_merged.csv")
daily2 = pd.read_csv("data/dailyActivity_merged (2).csv")

sleep = pd.read_csv("data/sleepDay_merged.csv")

hsteps1 = pd.read_csv("data/hourlySteps_merged.csv")
hsteps2 = pd.read_csv("data/hourlySteps_merged (2).csv")

hcal1 = pd.read_csv("data/hourlyCalories_merged.csv")
hcal2 = pd.read_csv("data/hourlyCalories_merged (2).csv")

hint1 = pd.read_csv("data/hourlyIntensities_merged.csv")
hint2 = pd.read_csv("data/hourlyIntensities_merged (2).csv")

hr1 = pd.read_csv("data/heartrate_seconds_merged.csv")
hr2 = pd.read_csv("data/heartrate_seconds_merged (2).csv")

daily = pd.concat([daily1, daily2], ignore_index=True)
hourly_steps = pd.concat([hsteps1, hsteps2], ignore_index=True)
hourly_cal = pd.concat([hcal1, hcal2], ignore_index=True)
hourly_int = pd.concat([hint1, hint2], ignore_index=True)
hr = pd.concat([hr1, hr2], ignore_index=True)

# clean data columns
daily["ActivityDate"] = pd.to_datetime(daily["ActivityDate"])

sleep["SleepDay"] = pd.to_datetime(sleep["SleepDay"])
sleep["date"] = sleep["SleepDay"].dt.date

hourly_steps["ActivityHour"] = pd.to_datetime(hourly_steps["ActivityHour"])
hourly_steps["date"] = hourly_steps["ActivityHour"].dt.date

hourly_cal["ActivityHour"] = pd.to_datetime(hourly_cal["ActivityHour"])
hourly_cal["date"] = hourly_cal["ActivityHour"].dt.date

hourly_int["ActivityHour"] = pd.to_datetime(hourly_int["ActivityHour"])
hourly_int["date"] = hourly_int["ActivityHour"].dt.date

hr["Time"] = pd.to_datetime(hr["Time"], errors="coerce")
hr["date"] = hr["Time"].dt.date

# drop rows where datetime failed
hr = hr.dropna(subset=["date"])

# aggregate houly -> daily
# Hourly steps/calories/intensity are combined to create one daily value per user.
hourly_steps_daily = (
hourly_steps.groupby(["Id", "date"])["StepTotal"]
.sum()
.reset_index()
)

hourly_cal_daily = (
hourly_cal.groupby(["Id", "date"])["Calories"]
.sum()
.reset_index()
)

hourly_int_daily = (
hourly_int.groupby(["Id","date"])["TotalIntensity"]
.sum()
.reset_index()
)

# Heart rate -> daily features
# Second-level heart rate data is summarized into daily stats (avg, max, min, variability).
hr_daily = (
hr.groupby(["Id", "date"])["Value"]
.agg(
avg_hr="mean",
max_hr="max",
min_hr="min",
hr_std="std"
)
.reset_index()
)

hr_daily["hr_range"] = hr_daily["max_hr"] - hr_daily["min_hr"]

# Sleep features
# Sleep data is used to compute daily sleep hours and sleep efficiency.
sleep_daily = (
sleep.groupby(["Id","date"])
[["TotalMinutesAsleep","TotalTimeInBed"]]
.sum()
.reset_index()
)

sleep_daily["sleep_hours"] = sleep_daily["TotalMinutesAsleep"] / 60

sleep_daily["sleep_efficiency"] = (
sleep_daily["TotalMinutesAsleep"] /
sleep_daily["TotalTimeInBed"]
)

# Prepare daily dataset
# Important columns from the daily activity file are selected as main lifestyle features.
daily["date"] = daily["ActivityDate"].dt.date

daily_main = daily[
[
"Id",
"date",
"TotalSteps",
"Calories",
"VeryActiveMinutes",
"FairlyActiveMinutes",
"LightlyActiveMinutes",
"SedentaryMinutes",
]
]

# meage
df = daily_main.merge(hourly_cal_daily, on=["Id", "date"], how="left")
df = df.merge(hourly_int_daily, on=["Id", "date"], how="left")
df = df.merge(hr_daily, on=["Id", "date"], how="left")
df = df.merge(sleep_daily, on=["Id", "date"], how="left")

df = df.drop_duplicates(subset=["Id","date"])

# missing values
# fill sleep
df["sleep_hours"] = df["sleep_hours"].fillna(df["sleep_hours"].median())
df["sleep_efficiency"] = df["sleep_efficiency"].fillna(df["sleep_efficiency"].median())

# fill heart rate
df["hr_std"] = df["hr_std"].fillna(df["hr_std"].median())
df["avg_hr"] = df["avg_hr"].fillna(df["avg_hr"].median())
df["max_hr"] = df["max_hr"].fillna(df["max_hr"].median())
df["min_hr"] = df["min_hr"].fillna(df["min_hr"].median())
df["hr_range"] = df["hr_range"].fillna(df["hr_range"].median())

# fill activity
df["TotalIntensity"] = df["TotalIntensity"].fillna(df["TotalIntensity"].median())
print("Unique HR values:", df["avg_hr"].nunique())
print("Unique sleep values:", df["sleep_hours"].nunique())

df = df[df["TotalSteps"] > 0]

# mood score
df["mood_score"] = (
0.35 * (df["sleep_hours"]/8) +
0.25 * (df["VeryActiveMinutes"]/60) +
0.20 * (1 - df["SedentaryMinutes"]/1440) +
0.10 * (df["sleep_efficiency"]) +
0.10 * (1/(1+df["hr_std"]))
)

df["mood_score"] = (df["mood_score"] * 10).clip(0, 10)

# productivity score
df["productivity_score"] = (
0.5 * (df["VeryActiveMinutes"] + df["FairlyActiveMinutes"]) / 90
+ 0.3 * (df["sleep_hours"] / 8)
+ 0.2 * (1 - df["SedentaryMinutes"] / 1440)
)

df["productivity_score"] = (
df["productivity_score"] * 10
).clip(0, 10)

# cleaning duplicate features
df = df.drop(columns=["StepTotal"], errors="ignore")
df = df.drop(columns=["Calories_y"])
df = df.rename(columns={"Calories_x": "Calories"})

print(df.head())
print(df.describe())

df.to_csv("data/fitbit_final_dataset.csv", index=False)

print("Final dataset created")
print("Dataset shape:", df.shape)
print(df.head())