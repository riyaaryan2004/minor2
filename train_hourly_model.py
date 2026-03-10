import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ---------------- LOAD DATA ----------------

hourly = pd.read_csv("data/hourly_data.csv")
daily = pd.read_csv("data/daily_data.csv")

# remove days without mood
daily = daily.dropna(subset=["mood_score"])

daily["mood_score"] = pd.to_numeric(daily["mood_score"])

# ---------------- MERGE DATA ----------------

df = hourly.merge(
    daily[["date","mood_score"]],
    on="date",
    how="inner"
)

print("Merged dataset size:", df.shape)

# ---------------- CLEAN DATA ----------------

df = df.dropna()

# ---------------- FEATURES ----------------

features = [
    "hour",
    "avg_hr",
    "hr_std",
    "steps",
    "hr_relative",
    "day_of_week"
]

X = df[features]
y = df["mood_score"]

# ---------------- SCALING ----------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# ---------------- TRAIN TEST SPLIT ----------------

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42
)

# ---------------- MODEL ----------------

rf = RandomForestRegressor(n_estimators=200)

rf.fit(X_train, y_train)

pred = rf.predict(X_test)

# ---------------- EVALUATION ----------------

mae = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))

print("\nHourly Model Results")
print("MAE:", mae)
print("RMSE:", rmse)

# ---------------- GRAPH ----------------

plt.figure()

plt.scatter(y_test, pred)

plt.xlabel("Actual Mood")
plt.ylabel("Predicted Mood")

plt.title("Hourly Model Prediction")

plt.show()