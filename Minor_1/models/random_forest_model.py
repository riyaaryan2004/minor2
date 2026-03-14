from train_model import (
    X_train, X_test,
    y_train_mood, y_test_mood,
    y_train_prod, y_test_prod,
    feature_names
)

from sklearn.model_selection import cross_val_score, RepeatedKFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

import json
from datetime import datetime
import joblib
import os
import numpy as np


# ---------------- MOOD MODEL ----------------

mood_model = RandomForestRegressor(
    n_estimators=150,
    max_depth=4,
    min_samples_split=6,
    min_samples_leaf=2,
    random_state=42
)

mood_model.fit(X_train, y_train_mood)

pred_mood = mood_model.predict(X_test)


# Mood Metrics
r2_mood = r2_score(y_test_mood, pred_mood)
rmse_mood = np.sqrt(mean_squared_error(y_test_mood, pred_mood))
mae_mood = mean_absolute_error(y_test_mood, pred_mood)

print("\nRandom Forest Mood Results")
print("R2:", r2_mood)
print("RMSE:", rmse_mood)
print("MAE:", mae_mood)


# ---------------- PRODUCTIVITY MODEL ----------------

prod_model = RandomForestRegressor(
    n_estimators=150,
    max_depth=4,
    min_samples_split=6,
    min_samples_leaf=2,
    random_state=42
)

prod_model.fit(X_train, y_train_prod)

pred_prod = prod_model.predict(X_test)


# Productivity Metrics
r2_prod = r2_score(y_test_prod, pred_prod)
rmse_prod = np.sqrt(mean_squared_error(y_test_prod, pred_prod))
mae_prod = mean_absolute_error(y_test_prod, pred_prod)

print("\nRandom Forest Productivity Results")
print("R2:", r2_prod)
print("RMSE:", rmse_prod)
print("MAE:", mae_prod)


# ---------------- CROSS VALIDATION ----------------

cv = RepeatedKFold(
    n_splits=3,
    n_repeats=10,
    random_state=42
)

mood_scores = cross_val_score(
    mood_model,
    X_train,
    y_train_mood,
    cv=cv,
    scoring="r2"
)

prod_scores = cross_val_score(
    prod_model,
    X_train,
    y_train_prod,
    cv=cv,
    scoring="r2"
)

print("\nMood CV Scores:", mood_scores)
print("Mood CV Average:", mood_scores.mean())

print("\nProductivity CV Scores:", prod_scores)
print("Productivity CV Average:", prod_scores.mean())


# ---------------- FEATURE IMPORTANCE ----------------

print("\nMood Feature Importance")

mood_importance = mood_model.feature_importances_

for name, score in sorted(
    zip(feature_names, mood_importance),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{name}: {score:.4f}")


print("\nProductivity Feature Importance")

prod_importance = prod_model.feature_importances_

for name, score in sorted(
    zip(feature_names, prod_importance),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{name}: {score:.4f}")


# ---------------- SAVE MODELS ----------------

os.makedirs("saved_models", exist_ok=True)

joblib.dump(mood_model, "saved_models/random_forest_mood.pkl")
joblib.dump(prod_model, "saved_models/random_forest_productivity.pkl")

print("\nModels saved successfully")


# ---------------- SAVE RESULTS ----------------

os.makedirs("results", exist_ok=True)

json_file = "results/model_results.json"
txt_file = "results/model_results.txt"


results_data = {
    "model": "RandomForest",
    "timestamp": datetime.now().isoformat(),

    "mood": {
        "test_r2": float(r2_mood),
        "test_rmse": float(rmse_mood),
        "test_mae": float(mae_mood),
        "cv_r2_mean": float(mood_scores.mean())
    },

    "productivity": {
        "test_r2": float(r2_prod),
        "test_rmse": float(rmse_prod),
        "test_mae": float(mae_prod),
        "cv_r2_mean": float(prod_scores.mean())
    }
}


# JSON UPDATE
if os.path.exists(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
else:
    data = {}

data["RandomForest"] = results_data

with open(json_file, "w") as f:
    json.dump(data, f, indent=4)

print("JSON results updated")


# TEXT UPDATE
entry = f"""
Model: RandomForest
Time: {results_data['timestamp']}

Mood Model
R2: {r2_mood}
RMSE: {rmse_mood}
MAE: {mae_mood}
CV Mean R2: {mood_scores.mean()}

Productivity Model
R2: {r2_prod}
RMSE: {rmse_prod}
MAE: {mae_prod}
CV Mean R2: {prod_scores.mean()}

-----------------------------------
"""

if os.path.exists(txt_file):

    with open(txt_file, "r") as f:
        content = f.read()

    if "Model: RandomForest" in content:
        parts = content.split("Model: RandomForest")
        new_content = parts[0]
    else:
        new_content = content

    with open(txt_file, "w") as f:
        f.write(new_content + entry)

else:
    with open(txt_file, "w") as f:
        f.write(entry)

print("Text results updated")
