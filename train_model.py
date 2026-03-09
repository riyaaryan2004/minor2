import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt


df = pd.read_csv("data/daily_data.csv")

print("Dataset loaded:")
print(df)

df = df[df["mood_score"].notna()]
df["mood_score"] = df["mood_score"].astype(float)
df["productivity_score"] = df["productivity_score"].astype(float)


features = [
    "total_sleep",
    "sleep_deficit",
    "total_steps",
    "hr_std_day"
]

X = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

y_mood = df["mood_score"]

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_mood,
    test_size=0.3,
    random_state=42
)

model = Ridge(alpha=10)
model.fit(X_train, y_train)

print("\nMood Model trained successfully")

pred_mood = model.predict(X_test)

pred_mood = np.clip(pred_mood,1,10)
pred_mood = np.round(pred_mood,1)

mood_results = pd.DataFrame({
    "Date": df.loc[y_test.index,"date"],
    "Actual Mood": y_test,
    "Predicted Mood": pred_mood
})

print("\nMood Prediction Results:")
print(mood_results)

mae = mean_absolute_error(y_test,pred_mood)
rmse = np.sqrt(mean_squared_error(y_test,pred_mood))
r2 = r2_score(y_test,pred_mood)

print("\nMood Evaluation Metrics:")
print("MAE:",mae)
print("RMSE:",rmse)
print("R2 Score:",r2)

y_prod = df["productivity_score"]

X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(
    X_scaled, y_prod,
    test_size=0.3,
    random_state=42
)

model_prod = Ridge(alpha=10)
model_prod.fit(X_train_p, y_train_p)

print("\nProductivity Model trained successfully")

pred_prod = model_prod.predict(X_test_p)

pred_prod = np.clip(pred_prod,1,10)
pred_prod = np.round(pred_prod,1)

prod_results = pd.DataFrame({
    "Date": df.loc[y_test_p.index,"date"],
    "Actual Productivity": y_test_p,
    "Predicted Productivity": pred_prod
})

print("\nProductivity Prediction Results:")
print(prod_results)

mae_p = mean_absolute_error(y_test_p,pred_prod)
rmse_p = np.sqrt(mean_squared_error(y_test_p,pred_prod))
r2_p = r2_score(y_test_p,pred_prod)

print("\nProductivity Evaluation Metrics:")
print("MAE:",mae_p)
print("RMSE:",rmse_p)
print("R2 Score:",r2_p)

coeff = pd.DataFrame({
    "Feature": features,
    "Coefficient": model.coef_
})

print("\nFeature Influence on Mood:")
print(coeff)

plt.scatter(df["total_sleep"], df["mood_score"])
plt.xlabel("Sleep (minutes)")
plt.ylabel("Mood Score")
plt.title("Sleep vs Mood")
plt.show()