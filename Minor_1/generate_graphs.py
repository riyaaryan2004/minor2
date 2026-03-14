import pandas as pd
import matplotlib.pyplot as plt
import os
import joblib

from models.train_model import (
    X_test,
    y_test_mood,
    y_test_prod
)

# load models
mood_model = joblib.load("saved_models/catboost_mood.pkl")
prod_model = joblib.load("saved_models/random_forest_productivity.pkl")

# predictions
mood_pred = mood_model.predict(X_test)
prod_pred = prod_model.predict(X_test)


# create folder
os.makedirs("graphs", exist_ok=True)

# load dataset
df = pd.read_csv("data/daily_data.csv")


# -------------------------
# 1 Mood distribution
# -------------------------
plt.figure()
plt.hist(df["mood_score"], bins=10)
plt.title("Mood Score Distribution")
plt.xlabel("Mood Score")
plt.ylabel("Frequency")
plt.grid(alpha=0.3)

plt.savefig("graphs/mood_distribution.png")
plt.close()


# -------------------------
# 2 Productivity distribution
# -------------------------
plt.figure()
plt.hist(df["productivity_score"], bins=10)
plt.title("Productivity Score Distribution")
plt.xlabel("Productivity Score")
plt.ylabel("Frequency")
plt.grid(alpha=0.3)

plt.savefig("graphs/productivity_distribution.png")
plt.close()


# -------------------------
# 3 Sleep vs Mood
# -------------------------
plt.figure()
plt.scatter(df["sleep_hours"], df["mood_score"])
plt.title("Sleep Hours vs Mood Score")
plt.xlabel("Sleep Hours")
plt.ylabel("Mood Score")
plt.grid(alpha=0.3)

plt.savefig("graphs/sleep_vs_mood.png")
plt.close()


# -------------------------
# 4 Steps vs Productivity
# -------------------------
plt.figure()
plt.scatter(df["total_steps"], df["productivity_score"])
plt.title("Steps vs Productivity")
plt.xlabel("Total Steps")
plt.ylabel("Productivity Score")
plt.grid(alpha=0.3)

plt.savefig("graphs/steps_vs_productivity.png")
plt.close()


# -------------------------
# 5 Stress vs Mood
# -------------------------
plt.figure()
plt.scatter(df["stress_index"], df["mood_score"])
plt.title("Stress Index vs Mood Score")
plt.xlabel("Stress Index")
plt.ylabel("Mood Score")
plt.grid(alpha=0.3)

plt.savefig("graphs/stress_vs_mood.png")
plt.close()


# -------------------------
# 6 Correlation Heatmap
# -------------------------
corr = df.corr(numeric_only=True)

plt.figure(figsize=(10,8))
plt.imshow(corr, cmap="coolwarm", aspect="auto")

plt.colorbar()
plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
plt.yticks(range(len(corr.columns)), corr.columns)

plt.title("Feature Correlation Heatmap")

plt.tight_layout()
plt.savefig("graphs/correlation_heatmap.png")
plt.close()


# -------------------------
# 7 All Feature Distributions
# -------------------------
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
    "activity_load"
]

rows = 3
cols = 4

plt.figure(figsize=(16,10))

for i, feature in enumerate(features):
    plt.subplot(rows, cols, i+1)
    plt.hist(df[feature], bins=10)
    plt.title(feature)

plt.tight_layout()
plt.savefig("graphs/feature_distributions.png")
plt.close()


# -------------------------
# 8 Mood Predicted vs Actual
# -------------------------
plt.figure()

plt.scatter(y_test_mood, mood_pred)
plt.plot([1,10],[1,10])

plt.xlabel("Actual Mood Score")
plt.ylabel("Predicted Mood Score")
plt.title("Predicted vs Actual Mood")

plt.savefig("graphs/mood_pred_vs_actual.png")
plt.close()


# -------------------------
# 9 Productivity Predicted vs Actual
# -------------------------
plt.figure()

plt.scatter(y_test_prod, prod_pred)
plt.plot([1,10],[1,10])

plt.xlabel("Actual Productivity Score")
plt.ylabel("Predicted Productivity Score")
plt.title("Predicted vs Actual Productivity")

plt.savefig("graphs/productivity_pred_vs_actual.png")
plt.close()


print("All graphs saved in graphs folder")
