import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.ensemble import RandomForestRegressor
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor

# ===============================
# Load dataset
# ===============================

df = pd.read_csv("data/fitbit_final_dataset.csv")# ===============================
# Features and Targets
# ===============================

features = [
    "TotalSteps",
    "VeryActiveMinutes",
    "FairlyActiveMinutes",
    "LightlyActiveMinutes",
    "SedentaryMinutes",
    "TotalIntensity",
    "sleep_hours",
    "sleep_efficiency",
    "avg_hr",
    "hr_std"
]

X = df[features]

y_mood = df["mood_score"]
y_prod = df["productivity_score"]

# ===============================
# Train Test Split
# ===============================

X_train, X_test, y_train, y_test = train_test_split(
    X, y_mood, test_size=0.2, random_state=42
)

# ===============================
# Models
# ===============================

models = {
    "RandomForest": RandomForestRegressor(
        n_estimators=200,
        random_state=42
    ),

    "CatBoost": CatBoostRegressor(
        iterations=500,
        depth=6,
        learning_rate=0.05,
        verbose=0
    ),

    "LightGBM": LGBMRegressor(
        n_estimators=500,
        learning_rate=0.05
    )
}

# ===============================
# Train + Evaluate
# ===============================

results = []

for name, model in models.items():

    print(f"Training {name}...")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    results.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })

    # save model
    joblib.dump(model, f"models/{name}_mood_model.pkl")

# ===============================
# Train Productivity Models
# ===============================

X_train, X_test, y_train, y_test = train_test_split(
    X, y_prod, test_size=0.2, random_state=42
)

for name, model in models.items():

    print(f"Training {name} for productivity...")

    model.fit(X_train, y_train)

    joblib.dump(model, f"models/{name}_productivity_model.pkl")

# ===============================
# Results DataFrame
# ===============================

results_df = pd.DataFrame(results)

print(results_df)

# ===============================
# Save comparison to TXT
# ===============================

with open("results/model_comparison.txt", "w") as f:

    f.write("MODEL COMPARISON RESULTS\n")
    f.write("========================\n\n")

    for _, row in results_df.iterrows():

        f.write(f"Model: {row['Model']}\n")
        f.write(f"MAE: {row['MAE']:.4f}\n")
        f.write(f"RMSE: {row['RMSE']:.4f}\n")
        f.write(f"R2 Score: {row['R2']:.4f}\n")
        f.write("\n")

print("Models saved successfully")
print("Comparison saved to model_comparison.txt")