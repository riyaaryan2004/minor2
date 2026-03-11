import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# ---------------- LOAD DATA ----------------

df = pd.read_csv("data/daily_data.csv")

print("Dataset shape:", df.shape)
print(df.head())

# ---------------- CLEAN DATA ----------------

# remove rows without mood labels
df = df.dropna(subset=["mood_score"])

# convert to numeric
df["mood_score"] = pd.to_numeric(df["mood_score"])

# ---------------- FEATURE SELECTION ----------------

features = [
    "resting_hr",
    "total_steps",
    "sleep_hours",
    "deep_ratio",
    "rem_ratio",
    "sleep_deficit",
    "avg_hr_day",
    "hr_std_day",
    "hr_deviation",
    "stress_index",
    "activity_load",
    "is_weekend"
]

X = df[features]
y = df["mood_score"]

print("\nFeatures used:")
print(X.columns)

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

print("\nTrain size:", X_train.shape)
print("Test size:", X_test.shape)

# ---------------- MODELS ----------------

lr = LinearRegression()
rf = RandomForestRegressor(n_estimators=200, random_state=42)

# train models
lr.fit(X_train, y_train)
rf.fit(X_train, y_train)

# ---------------- PREDICTIONS ----------------

lr_pred = lr.predict(X_test)
rf_pred = rf.predict(X_test)

# ---------------- EVALUATION ----------------

def evaluate(name, y_true, y_pred):

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    print(f"\n{name} Results")
    print("MAE:", mae)
    print("RMSE:", rmse)
    print("R2:", r2)

evaluate("Linear Regression", y_test, lr_pred)
evaluate("Random Forest", y_test, rf_pred)

# ---------------- GRAPH: ACTUAL VS PREDICTED ----------------

plt.figure()

plt.scatter(y_test, rf_pred)
plt.xlabel("Actual Mood")
plt.ylabel("Predicted Mood")
plt.title("Actual vs Predicted Mood (RandomForest)")

plt.show()

# ---------------- FEATURE IMPORTANCE ----------------

importance = rf.feature_importances_

plt.figure()

plt.barh(features, importance)
plt.xlabel("Importance")
plt.title("Feature Importance")

plt.show()