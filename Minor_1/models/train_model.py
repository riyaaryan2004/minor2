import pandas as pd

df = pd.read_csv("data/daily_data.csv")

print("Original Shape:", df.shape)

# Sort by date so time order maintain rahe
df = df.sort_values("date")

# Remove unnecessary columns
df = df.drop(columns=[
    "date",
    "sleep_start_time",
    "wake_time",
    "sleep_midpoint"
])

# Remove missing rows
df = df.dropna()

print("Clean Shape:", df.shape)

# Features
X = df.drop(columns=["mood_score","productivity_score"])

# Targets
y_mood = df["mood_score"]
y_prod = df["productivity_score"]

feature_names = X.columns

print("Total Input Features:", X.shape[1])
print("Features:", list(feature_names))

# TIME-BASED SPLIT

split_index = int(len(X) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train_mood = y_mood.iloc[:split_index]
y_test_mood = y_mood.iloc[split_index:]

y_train_prod = y_prod.iloc[:split_index]
y_test_prod = y_prod.iloc[split_index:]

print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])
