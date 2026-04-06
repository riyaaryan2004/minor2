from train_model import (
    X_train, X_test,
    y_train_mood, y_test_mood,
    y_train_prod, y_test_prod,
    feature_names,
    w_train   # ✅ added
)

from sklearn.model_selection import cross_val_score, RepeatedKFold   # ✅ updated
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

import json
from datetime import datetime
import joblib
import os
import numpy as np


# ✅ BASE DIR FIX
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------- MOOD MODEL ----------------

mood_model = RandomForestRegressor(
    n_estimators=150,
    max_depth=4,
    min_samples_split=6,
    min_samples_leaf=2,
    random_state=42
)

mood_model.fit(X_train, y_train_mood, sample_weight=w_train)  # ✅ added

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

prod_model.fit(X_train, y_train_prod, sample_weight=w_train)  # ✅ added

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

cv = RepeatedKFold(   # ✅ aligned with LightGBM
    n_splits=5,
    n_repeats=10,
    random_state=42
)

mood_scores = cross_val_score(
    mood_model,   # ✅ same model
    X_train,
    y_train_mood,
    cv=cv,
    scoring="r2"
)

prod_scores = cross_val_score(
    prod_model,   # ✅ same model
    X_train,
    y_train_prod,
    cv=cv,
    scoring="r2"
)

print("\nMood CV Scores:", mood_scores)
print("Mood CV Average:", mood_scores.mean())
print("\nTrain R2 (Mood):", mood_model.score(X_train, y_train_mood))

print("\nProductivity CV Scores:", prod_scores)
print("Productivity CV Average:", prod_scores.mean())
print("\nTrain R2 (Productivity):", prod_model.score(X_train, y_train_prod))


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

model_dir = os.path.join(BASE_DIR, "saved_models")
os.makedirs(model_dir, exist_ok=True)

joblib.dump(mood_model, os.path.join(model_dir, "random_forest_mood.pkl"))
joblib.dump(prod_model, os.path.join(model_dir, "random_forest_productivity.pkl"))

print("\nModels saved successfully")


# ---------------- SAVE RESULTS ----------------

results_dir = os.path.join(BASE_DIR, "results")
os.makedirs(results_dir, exist_ok=True)

json_file = os.path.join(results_dir, "model_results.json")
txt_file = os.path.join(results_dir, "model_results.txt")


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