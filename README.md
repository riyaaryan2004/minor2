# 🧠 Fitbit Mood & Productivity Prediction System

## 📌 Overview

An end-to-end machine learning project that uses Fitbit heart-rate, sleep, and activity data to estimate daily mood and productivity. The main application combines a Flask backend, React dashboard, trained ML models, daily data repair/sync utilities, insights, alerts, and mood-aware movie recommendations.

The repository also includes an experimental ML workspace built from a Kaggle-style dataset for model comparison and exploration.

## Key Features

- Fitbit OAuth login and daily data sync
- Mood and productivity prediction from physiological features
- Heart-rate charts using saved hourly data and live Fitbit intraday data
- Stress, sleep, activity, and history-based insights
- Heart-rate alert workflow with acknowledgement/status endpoints
- Focus/task recommendation engine
- Mood-aware movie recommender with like/dislike profile storage
- Model training and evaluation scripts for multiple regressors
- Emergency email alerts to contacts using SendGrid
- Real-time heart rate anomaly detection with notifications


## Tech Stack

- Python, Flask, Flask-CORS
- Pandas, NumPy, Scikit-learn, Joblib
- LightGBM and CatBoost model files
- React, React Router, Chart.js
- Fitbit API

## Project Structure

```text
minor2/
+-- README.md
+-- .gitignore
+-- Minor_1/
|   +-- backend/
|   |   +-- app.py                    # Flask entry point
|   |   +-- config.py                 # Paths and Fitbit OAuth config
|   |   +-- alert_settings.py         # Heart alert configuration loader
|   |   +-- heart_alert_vars.py       # Heart alert defaults
|   |   +-- routes/
|   |   |   +-- auth_routes.py        # /login and /callback
|   |   |   +-- data_routes.py        # /rate, /sync-day, /activity, /alerts, /movies
|   |   |   +-- predict_routes.py     # /predict and /focus
|   |   |   +-- hr_routes.py          # /hr-data, /hr-minute, /hr-latest
|   |   |   +-- heart_alert_routes.py # /heart-alert/* endpoints
|   |   +-- services/                 # Fitbit, token, and alert services
|   |   +-- utils/                    # Shared backend utilities
|   +-- frontend/
|   |   +-- public/
|   |   +-- src/
|   |   |   +-- api/api.js
|   |   |   +-- components/
|   |   |   +-- App.js
|   |   +-- package.json              # Basic React dashboard
|   +-- frontend1/
|   |   +-- public/
|   |   +-- src/
|   |   |   +-- api/api.js
|   |   |   +-- components/
|   |   |   +-- App.js
|   |   +-- package.json              # Expanded React dashboard
|   +-- ml/
|       +-- data/                     # Daily, hourly, and evaluation CSV files
|       +-- docs/                     # Notes, steps, and result summaries
|       +-- features/                 # Prediction helpers, graphs, insights, recommender
|       +-- models/                   # Training scripts for ML models
|       +-- results/                  # Evaluation results
|       +-- saved_models/             # Trained .pkl model artifacts
|       +-- repair_day.py             # Fitbit daily data repair/sync utility
+-- Minor_2/
    +-- final_dataset.csv
    +-- prepare_dataset.py
    +-- graphs/
    +-- models/                       # Experimental model training scripts
```

## Setup

### 1. Python environment

Create and activate a Python virtual environment from the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the Python packages used by the backend and ML scripts:

```powershell
pip install flask flask-cors requests pandas numpy scikit-learn joblib matplotlib lightgbm catboost
```

Note: this repo does not currently include a `requirements.txt`, so the command above documents the expected packages.

### 2. Fitbit configuration

Fitbit OAuth settings are read from `Minor_1/backend/config.py`, including:

- `CLIENT_ID`
- `CLIENT_SECRET`
- `REDIRECT_URI`

For local development, the backend expects the redirect URI to be:

```text
http://localhost:5000/callback
```

Tokens are saved to `Minor_1/backend/token.txt`, which is ignored by Git.

### 3. Frontend dependencies

Install dependencies for the dashboard you want to run:

```powershell
cd Minor_1\frontend1
npm install
```

`frontend1` appears to be the fuller dashboard. `frontend` is also available as a smaller/basic React app.

## Running the Project

### 1. Start the Flask backend

Run this from the repository root:

```powershell
python Minor_1\backend\app.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://127.0.0.1:5000/
```

### 2. Start the React dashboard

In a second terminal:

```powershell
cd Minor_1\frontend1
npm start
```

The dashboard usually opens at:

```text
http://localhost:3000
```

The frontend API client points to `http://127.0.0.1:5000`.

## Main API Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Backend health check |
| `/login` | GET | Start Fitbit OAuth login |
| `/callback` | GET | Fitbit OAuth callback |
| `/sync-day?date=YYYY-MM-DD` | GET/POST | Fetch/repair Fitbit data for a day |
| `/rate?date=YYYY-MM-DD&mood=7&productivity=6` | GET | Save user mood/productivity labels |
| `/predict?date=YYYY-MM-DD` | GET | Predict mood, productivity, stress, sleep, and insights |
| `/focus` | POST | Recommend task focus based on current state |
| `/activity?date=YYYY-MM-DD` | GET | Activity suggestions |
| `/alerts?date=YYYY-MM-DD` | GET | Daily alerts |
| `/hr-data?date=YYYY-MM-DD` | GET | Saved hourly heart-rate data |
| `/hr-minute?date=YYYY-MM-DD` | GET | Live Fitbit intraday heart-rate data |
| `/hr-latest` | GET | Latest live or saved heart-rate value |
| `/heart-alert/config` | GET | Heart alert configuration |
| `/heart-alert/check` | POST | Create/check a heart-rate alert |
| `/heart-alert/acknowledge` | POST | Acknowledge an alert |
| `/heart-alert/status/<alert_id>` | GET | Read alert status |
| `/movies?date=YYYY-MM-DD` | GET | Mood-aware movie recommendations |
| `/movies/refresh` | GET | Clear movie recommendation cache |
| `/movies/like` | POST | Save liked movie |
| `/movies/dislike` | POST | Save disliked movie |
| `/movies/profile` | GET | Read movie preference profile |

## Common Workflows

### Login to Fitbit

```text
http://127.0.0.1:5000/login
```

### Sync today's Fitbit data

```text
http://127.0.0.1:5000/sync-day
```

### Sync a specific day

```text
http://127.0.0.1:5000/sync-day?date=2026-05-01
```

### Save mood and productivity labels

```text
http://127.0.0.1:5000/rate?date=2026-05-01&mood=7&productivity=6
```

### Train or refresh models

Run model scripts from `Minor_1` so imports resolve correctly:

```powershell
cd Minor_1
python -m ml.models.linear_regression_model
python -m ml.models.ridge_regression_model
python -m ml.models.random_forest_model
python -m ml.models.catboost_model
python -m ml.models.lightgbm_model
```

Saved model files are stored in:

```text
Minor_1/ml/saved_models/
```

## Models Used

- Linear Regression
- Ridge Regression
- Random Forest
- CatBoost
- LightGBM

LightGBM is used as the strongest final model in the current project notes.

## 📊 Results Summary

| Model             | Mood R²        | Productivity R² |
| ----------------- | -------------- | --------------- |
| LightGBM          | ⭐ Best (~0.68) | ⭐ Best (~0.59)  |
| Random Forest     | Good           | Good            |
| CatBoost          | Moderate       | Moderate        |
| Ridge             | Weak           | Weak            |
| Linear Regression | Poor           | Poor            |


## Data and Generated Files

Tracked important data:

- `Minor_1/ml/data/daily_data.csv`
- `Minor_1/ml/data/hourly_data.csv`
- `Minor_1/ml/data/evaluation_results.csv`
- `Minor_2/final_dataset.csv`

Ignored generated/local files include:

- Python virtual environments
- React `node_modules`
- `.env` files
- Fitbit `token.txt`
- Movie recommender cache/profile JSON
- Most generated images and CSV files
- Pickled model artifacts

## ⚠️ Limitations

* Small dataset size (~95 samples)
* Real-world data variability
* Limited generalization

## 🔮 Future Improvements

* Increase dataset size
* Add deep learning models
* Real-time prediction dashboard
* Personalized recommendations

## Notes

- Run the backend before opening the React dashboard.
- Use `frontend1` for the most complete UI.
- The project currently has no root `requirements.txt`; add one later if reproducible setup becomes important.
- This project is intended for academic use and demonstration of a complete ML pipeline.


## Contributors

- Gaurangi Agarwal
- Chhavi
- Riya Aryan
