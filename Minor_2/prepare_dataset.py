import pandas as pd
import numpy as np

# -------------------------------
# Utility
# -------------------------------

def load_concat(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    return pd.concat([df1, df2], ignore_index=True)


# -------------------------------
# STEP 1: PROCESS STEPS (HOURLY → DAILY)
# -------------------------------

def process_steps(hsteps):
    hsteps['ActivityHour'] = pd.to_datetime(hsteps['ActivityHour'])
    hsteps['date'] = hsteps['ActivityHour'].dt.date

    steps_daily = hsteps.groupby(['Id', 'date'])['StepTotal'].sum().reset_index()
    steps_daily.rename(columns={'StepTotal': 'total_steps'}, inplace=True)

    return steps_daily


# -------------------------------
# STEP 2: PROCESS INTENSITY (HOURLY → DAILY)
# -------------------------------

def process_intensity(hint):
    hint['ActivityHour'] = pd.to_datetime(hint['ActivityHour'])
    hint['date'] = hint['ActivityHour'].dt.date

    intensity_daily = hint.groupby(['Id', 'date'])['TotalIntensity'].sum().reset_index()
    intensity_daily.rename(columns={'TotalIntensity': 'activity_load'}, inplace=True)

    return intensity_daily


# -------------------------------
# STEP 3: PROCESS HEART RATE (SECONDS → DAILY)
# -------------------------------

def process_hr(hr):
    hr['Time'] = pd.to_datetime(hr['Time'])
    hr['date'] = hr['Time'].dt.date

    hr_daily = hr.groupby(['Id', 'date'])['Value'].agg(
        avg_hr_day='mean',
        hr_std_day='std'
    ).reset_index()

    return hr_daily


# -------------------------------
# STEP 4: PROCESS SLEEP (MINUTE → DAILY)
# -------------------------------

def process_sleep(msleep):
    msleep['date'] = pd.to_datetime(msleep['date']).dt.date

    sleep_daily = msleep.groupby(['Id', 'date'])['value'].sum().reset_index()

    sleep_daily.rename(columns={'value': 'total_sleep'}, inplace=True)
    sleep_daily['sleep_hours'] = sleep_daily['total_sleep'] / 60.0

    return sleep_daily


# -------------------------------
# STEP 5: PROCESS DAILY ACTIVITY
# -------------------------------

def process_daily(daily):
    daily['ActivityDate'] = pd.to_datetime(daily['ActivityDate'])
    daily['date'] = daily['ActivityDate'].dt.date

    daily_out = daily[['Id', 'date', 'Calories']].copy()

    return daily_out


# -------------------------------
# STEP 6: FEATURE ENGINEERING
# -------------------------------

def feature_engineering(df):

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['Id', 'date'])

    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    # HR deviation PER USER
    df['hr_deviation'] = df.groupby('Id')['avg_hr_day'].transform(
        lambda x: x - x.rolling(3).mean()
    )

    # Stress index
    df['stress_index'] = df['avg_hr_day'] / (df['hr_std_day'] + 1)

    # Sleep deficit
    df['sleep_deficit'] = 8 - df['sleep_hours']

    return df


# -------------------------------
# UPDATED CLEANING (🔥 FIXED ALL ISSUES)
# -------------------------------

def clean_data(df):

    # -------------------
    # REMOVE DUPLICATES (🔥 FIX)
    # -------------------
    df = df.drop_duplicates(subset=['Id', 'date'])

    # -------------------
    # STRONGER FILTERS (🔥 FIX)
    # -------------------
    df = df[(df['sleep_hours'].isna()) | ((df['sleep_hours'] >= 2) & (df['sleep_hours'] <= 12))]
    df = df[(df['total_steps'].isna()) | (df['total_steps'] >= 500)]

    # -------------------
    # DROP IMPORTANT MISSING
    # -------------------
    df = df.dropna(subset=['sleep_hours', 'total_steps'])

    # -------------------
    # HANDLE HR (better)
    # -------------------
    df['avg_hr_day'] = df.groupby('Id')['avg_hr_day'].transform(lambda x: x.fillna(x.mean()))
    df['hr_std_day'] = df.groupby('Id')['hr_std_day'].transform(lambda x: x.fillna(x.mean()))

    # If still NaN → fill global (last fallback)
    df['avg_hr_day'] = df['avg_hr_day'].fillna(df['avg_hr_day'].mean())
    df['hr_std_day'] = df['hr_std_day'].fillna(df['hr_std_day'].mean())

    # -------------------
    # NORMALIZATION (per user)
    # -------------------
    df['steps_norm'] = df.groupby('Id')['total_steps'].transform(
        lambda x: (x - x.mean()) / (x.std() + 1e-6)
    )

    df['sleep_norm'] = df.groupby('Id')['sleep_hours'].transform(
        lambda x: (x - x.mean()) / (x.std() + 1e-6)
    )

    # -------------------
    # 🔥 ADD LAG FEATURES (VERY IMPORTANT)
    # -------------------
    df = df.sort_values(['Id', 'date'])

    df['steps_prev1'] = df.groupby('Id')['total_steps'].shift(1)
    df['sleep_prev1'] = df.groupby('Id')['sleep_hours'].shift(1)

    df['steps_avg_3'] = df.groupby('Id')['total_steps'].transform(
        lambda x: x.rolling(3).mean()
    )

    df['sleep_avg_3'] = df.groupby('Id')['sleep_hours'].transform(
        lambda x: x.rolling(3).mean()
    )

    # Drop rows where lag not available
    df = df.dropna(subset=['steps_prev1', 'sleep_prev1'])

    # -------------------
    # EXTRA FEATURES (FINAL)
    # -------------------
    
    # 2. Sleep efficiency (FIXED VERSION)
    df['sleep_efficiency'] = df['sleep_hours'] / 8

    # 3. Stress + Sleep interaction (GOOD FEATURE)
    df['stress_sleep_interaction'] = df['stress_index'] * df['sleep_deficit']

    # 4. Recovery score (VERY IMPORTANT)
    df['recovery_score'] = df['sleep_hours'] / (df['activity_load'] + 1)

    # 5. Fatigue index (VERY USEFUL)
    df['fatigue_index'] = df['sleep_deficit'] + (df['activity_load'] / 500)

    # 6. Activity trend (TEMPORAL BEHAVIOR)
    df['activity_trend'] = df['total_steps'] - df['steps_prev1']

    # 7. Sleep consistency (routine stability)
    df['sleep_variation'] = df.groupby('Id')['sleep_hours'].transform(
        lambda x: x.rolling(3).std()
    )
    
    # -------------------
    # FINAL SAFETY FIXES
    # -------------------

    # 1. Fix sleep_variation NaN
    df['sleep_variation'] = df['sleep_variation'].fillna(0)

    # 2. Safe stress index
    df['stress_index'] = np.log1p(df['stress_index'].clip(lower=0))

    # 3. Activity load safety
    df['activity_load'] = df['activity_load'].fillna(0)
    
    return df


# -------------------------------
# STEP 7: MERGE EVERYTHING
# -------------------------------

def merge_all(daily, steps, hr, sleep, intensity):

    df = daily.copy()

    df = df.merge(steps, on=['Id', 'date'], how='left')
    df = df.merge(hr, on=['Id', 'date'], how='left')
    df = df.merge(sleep, on=['Id', 'date'], how='left')
    df = df.merge(intensity, on=['Id', 'date'], how='left')

    return df


# -------------------------------
# MAIN PIPELINE
# -------------------------------

def build_dataset():

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


    steps_daily = process_steps(hsteps)
    intensity_daily = process_intensity(hint)
    hr_daily = process_hr(hr)
    sleep_daily = process_sleep(msleep)
    daily_clean = process_daily(daily)


    final = merge_all(daily_clean, steps_daily, hr_daily, sleep_daily, intensity_daily)

    final = feature_engineering(final)

    final = clean_data(final)
    
    # -------------------
    # FIX NaNs BEFORE TARGETS
    # -------------------

    final['stress_index'] = final['stress_index'].fillna(0)
    final['sleep_norm'] = final['sleep_norm'].fillna(0)
    final['steps_norm'] = final['steps_norm'].fillna(0)
    final['sleep_deficit'] = final['sleep_deficit'].fillna(0)

    # -------------------
    # GENERATE MOOD SCORE
    # -------------------

    final['mood_score'] = (
        5
        + 1.5 * final['sleep_norm']
        + 1.2 * final['steps_norm']
        - 1.5 * final['stress_index']
        - 1.0 * final['sleep_deficit']
    )

    # Normalize to 1–10
    final['mood_score'] = final['mood_score'].clip(1, 10)


    # -------------------
    # GENERATE PRODUCTIVITY
    # -------------------

    final['productivity_score'] = (
        5
        + 1.5 * final['steps_norm']
        + 1.0 * final['activity_load'] / 100
        - 1.2 * final['fatigue_index']
    )

    final['productivity_score'] = final['productivity_score'].clip(1, 10)

    final.to_csv("final_dataset.csv", index=False)

    print("✅ FINAL CLEAN + TEMPORAL DATASET READY!")


# -------------------------------
# RUN
# -------------------------------

if __name__ == "__main__":
    build_dataset()