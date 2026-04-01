import os
import json
import joblib
import numpy as np
from datetime import datetime

from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import Ridge

from catboost import CatBoostRegressor

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

# ---------------- MODEL CONFIG ----------------
def get_model():
    return CatBoostRegressor(
        iterations=300,
        depth=3,
        learning_rate=0.03,
        l2_leaf_reg=5,
        loss_function="RMSE",
        verbose=False,
        random_seed=42
    )

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

# ---------------- MOOD MODEL ----------------
mood_model = get_model()
mood_model.fit(X_train, y_train_mood)

pred_mood = mood_model.predict(X_test)

r2_mood = r2_score(y_test_mood, pred_mood)
rmse_mood = np.sqrt(mean_squared_error(y_test_mood, pred_mood))
mae_mood = mean_absolute_error(y_test_mood, pred_mood)

print("\n🐱 CatBoost Mood Results")
print("R2:", r2_mood)
print("RMSE:", rmse_mood)
print("MAE:", mae_mood)

# ---------------- PRODUCTIVITY MODEL ----------------
prod_model = get_model()
prod_model.fit(X_train, y_train_prod)

pred_prod = prod_model.predict(X_test)

r2_prod = r2_score(y_test_prod, pred_prod)
rmse_prod = np.sqrt(mean_squared_error(y_test_prod, pred_prod))
mae_prod = mean_absolute_error(y_test_prod, pred_prod)

print("\n🐱 CatBoost Productivity Results")
print("R2:", r2_prod)
print("RMSE:", rmse_prod)
print("MAE:", mae_prod)

# ---------------- TIME SERIES CV ----------------
tscv = TimeSeriesSplit(n_splits=5)

mood_scores = cross_val_score(get_model(), X_train, y_train_mood, cv=tscv, scoring="r2")
prod_scores = cross_val_score(get_model(), X_train, y_train_prod, cv=tscv, scoring="r2")

print("\nMood CV Mean:", mood_scores.mean())
print("Productivity CV Mean:", prod_scores.mean())

# ---------------- BASELINE ----------------
ridge_mood = Ridge().fit(X_train, y_train_mood)
ridge_prod = Ridge().fit(X_train, y_train_prod)

ridge_r2_mood = r2_score(y_test_mood, ridge_mood.predict(X_test))
ridge_r2_prod = r2_score(y_test_prod, ridge_prod.predict(X_test))

print("\nBaseline Ridge Mood:", ridge_r2_mood)
print("Baseline Ridge Prod:", ridge_r2_prod)

# ---------------- FEATURE IMPORTANCE ----------------
print("\n🔥 Feature Importance")

for name, score in sorted(
    zip(feature_names, mood_model.get_feature_importance()),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{name}: {score:.4f}")

# ---------------- SAVE MODELS ----------------
model_dir = os.path.join(BASE_DIR, "saved_models")
os.makedirs(model_dir, exist_ok=True)

joblib.dump(mood_model, os.path.join(model_dir, "catboost_mood.pkl"))
joblib.dump(prod_model, os.path.join(model_dir, "catboost_productivity.pkl"))

print("\n✅ Models saved")

# ---------------- SAVE RESULTS ----------------
results_dir = os.path.join(BASE_DIR, "results")
os.makedirs(results_dir, exist_ok=True)

json_file = os.path.join(results_dir, "model_results.json")

results_data = {
    "model": "CatBoost",
    "timestamp": datetime.now().isoformat(),
    "mood": {
        "r2": float(r2_mood),
        "cv_mean": float(mood_scores.mean()),
        "baseline": float(ridge_r2_mood)
    },
    "productivity": {
        "r2": float(r2_prod),
        "cv_mean": float(prod_scores.mean()),
        "baseline": float(ridge_r2_prod)
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

data["CatBoost"] = results_data

with open(json_file, "w") as f:
    json.dump(data, f, indent=4)

print("📁 Results saved")