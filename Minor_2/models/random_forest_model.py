import os
import json
import joblib
import numpy as np
from datetime import datetime

from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# ---------------- IMPORT DATA ----------------
from train_model import (
    X_train, X_test,
    y_train_mood, y_test_mood,
    y_train_prod, y_test_prod,
    feature_names
)

# ---------------- BASE DIR ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- SAFETY ----------------
X_train = X_train.fillna(0)
X_test = X_test.fillna(0)

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

r2_mood = r2_score(y_test_mood, pred_mood)
rmse_mood = np.sqrt(mean_squared_error(y_test_mood, pred_mood))
mae_mood = mean_absolute_error(y_test_mood, pred_mood)

print("\n🌲 Random Forest Mood Results")
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

r2_prod = r2_score(y_test_prod, pred_prod)
rmse_prod = np.sqrt(mean_squared_error(y_test_prod, pred_prod))
mae_prod = mean_absolute_error(y_test_prod, pred_prod)

print("\n🌲 Random Forest Productivity Results")
print("R2:", r2_prod)
print("RMSE:", rmse_prod)
print("MAE:", mae_prod)

# ---------------- TIME SERIES CV ----------------
tscv = TimeSeriesSplit(n_splits=5)

mood_scores = cross_val_score(mood_model, X_train, y_train_mood, cv=tscv, scoring="r2")
prod_scores = cross_val_score(prod_model, X_train, y_train_prod, cv=tscv, scoring="r2")

print("\nMood CV Mean:", mood_scores.mean())
print("Productivity CV Mean:", prod_scores.mean())

# ---------------- FEATURE IMPORTANCE ----------------
print("\n🔥 Feature Importance")

for name, score in sorted(
    zip(feature_names, mood_model.feature_importances_),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{name}: {score:.4f}")

# ---------------- SAVE MODELS ----------------
model_dir = os.path.join(BASE_DIR, "saved_models")
os.makedirs(model_dir, exist_ok=True)

joblib.dump(mood_model, os.path.join(model_dir, "random_forest_mood.pkl"))
joblib.dump(prod_model, os.path.join(model_dir, "random_forest_productivity.pkl"))

print("\n✅ Models saved")

# ---------------- SAVE RESULTS ----------------
results_dir = os.path.join(BASE_DIR, "results")
os.makedirs(results_dir, exist_ok=True)

json_file = os.path.join(results_dir, "model_results.json")

results_data = {
    "model": "RandomForest",
    "timestamp": datetime.now().isoformat(),
    "mood": {
        "r2": float(r2_mood),
        "cv_mean": float(mood_scores.mean())
    },
    "productivity": {
        "r2": float(r2_prod),
        "cv_mean": float(prod_scores.mean())
    }
}

if os.path.exists(json_file):
    with open(json_file, "r") as f:
        try:
            data = json.load(f)
        except:
            data = {}
else:
    data = {}

data["RandomForest"] = results_data

with open(json_file, "w") as f:
    json.dump(data, f, indent=4)

print("📁 Results saved")