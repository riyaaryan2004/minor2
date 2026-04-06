# 🧠 Fitbit Mood & Productivity Prediction System

## 📌 Overview

This project is an end-to-end machine learning system that predicts a user's **daily mood and productivity** using Fitbit physiological data such as heart rate, sleep, and activity.

It also includes:

* Real-time data collection from Fitbit API
* Feature engineering from physiological signals
* Multiple ML models for prediction
* Movie recommendation system based on mood

---

## 🚀 Features

* 📊 Daily mood prediction using ML models
* ⚡ Productivity estimation
* ❤️ Heart rate & stress analysis
* 💤 Sleep pattern analysis
* 🎬 Mood-based movie recommendation
* 📈 Data visualization (HR graphs)
* 🔁 Automated daily data collection

---

## 🛠️ Tech Stack

* Python
* Flask (Backend server)
* Pandas, NumPy (Data processing)
* Scikit-learn (ML models)
* LightGBM, CatBoost
* Fitbit API

---

## 📂 Project Structure

```
Minor_1/
│
├── data/                  # Daily & hourly datasets
├── features/              # Feature engineering scripts
├── models/                # ML model implementations
├── results/               # Model evaluation outputs
├── saved_models/          # Trained model files (.pkl)
├── docs/                  # Logs / instructions / outputs
│
├── app.py                 # Flask server (main entry point)
├── repair_day.py          # Fix missing/corrupted day data
├── README.md              # Project documentation
```

---

## ⚙️ How to Run the Project

### 1. Start Server

```
python app.py
```

Server runs at:
http://localhost:5000

---

### 2. Collect Data

Open in browser:

```
http://localhost:5000/login
```

This will:

* Fetch heart rate data
* Fetch steps
* Fetch sleep data
* Update datasets

---

### 3. Enter Mood & Productivity

```
http://localhost:5000/rate?mood=7&productivity=6
```

---

### 4. Train Models

```
python train_model.py
python lightgbm_model.py
python random_forest_model.py
python ridge_model.py
python catboost_model.py
```

---

### 5. Run Movie Recommender

```
python movie_recommendor.py
```

---

## 🤖 Models Used

* Linear Regression (Baseline)
* Ridge Regression
* Random Forest
* CatBoost
* LightGBM (**Final Model**)

---

## 📊 Results Summary

| Model             | Mood R²        | Productivity R² |
| ----------------- | -------------- | --------------- |
| LightGBM          | ⭐ Best (~0.68) | ⭐ Best (~0.59)  |
| Random Forest     | Good           | Good            |
| CatBoost          | Moderate       | Moderate        |
| Ridge             | Weak           | Weak            |
| Linear Regression | Poor           | Poor            |

---

## 🏆 Final Model

**LightGBM** was selected as the final model because:

* Highest prediction accuracy
* Handles non-linear relationships
* Performs well on small datasets

---

## 🧠 Key Insights

* Stress and sleep deficit strongly impact mood
* Activity has moderate influence
* Physiological signals are noisy but useful

---

## ⚠️ Limitations

* Small dataset size (~95 samples)
* Real-world data variability
* Limited generalization

---

## 🔮 Future Improvements

* Increase dataset size
* Add deep learning models
* Real-time prediction dashboard
* Personalized recommendations

---

## 📌 Note

This project is built for academic purposes and demonstrates a complete ML pipeline from data collection to deployment.
