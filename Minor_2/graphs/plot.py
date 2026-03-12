import os
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("../data/fitbit_final_dataset.csv")

print(df.head())
print(df.shape)
print(df.info())
print(df.describe())
print(df.isnull().sum())

# -----------------------------
# Create folder for plots
# -----------------------------
plot_dir = "plots"
os.makedirs(plot_dir, exist_ok=True)

# -----------------------------
# Get numeric columns
# -----------------------------
numeric_cols = df.select_dtypes(include=["float64","int64"]).columns

# -----------------------------
# 1. Feature Distribution (ALL in one image)
# -----------------------------
cols = list(numeric_cols)

n = len(cols)
ncols = 4
nrows = math.ceil(n / ncols)

fig, axes = plt.subplots(nrows, ncols, figsize=(16, 4*nrows))
axes = axes.flatten()

for i, col in enumerate(cols):
    sns.histplot(df[col], bins=30, kde=True, ax=axes[i])
    axes[i].set_title(col)

# remove empty plots if any
for j in range(i+1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.savefig(f"{plot_dir}/all_feature_distributions.png")
plt.close()

# -----------------------------
# 2. Combined Boxplot (ALL features)
# -----------------------------
plt.figure(figsize=(14,6))
sns.boxplot(data=df[numeric_cols])
plt.xticks(rotation=45)
plt.title("All Feature Boxplots")
plt.tight_layout()
plt.savefig(f"{plot_dir}/all_features_boxplot.png")
plt.close()

# -----------------------------
# 3. Correlation Heatmap
# -----------------------------
plt.figure(figsize=(12,8))
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm")
plt.title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig(f"{plot_dir}/correlation_heatmap.png")
plt.close()

# -----------------------------
# 4. Mood vs Productivity
# -----------------------------
plt.figure(figsize=(6,5))
sns.scatterplot(x=df["mood_score"], y=df["productivity_score"])
plt.title("Mood vs Productivity")
plt.tight_layout()
plt.savefig(f"{plot_dir}/mood_vs_productivity.png")
plt.close()

# -----------------------------
# 5. Steps vs Mood
# -----------------------------
plt.figure(figsize=(6,5))
sns.scatterplot(x=df["TotalSteps"], y=df["mood_score"])
plt.title("Steps vs Mood")
plt.tight_layout()
plt.savefig(f"{plot_dir}/steps_vs_mood.png")
plt.close()

# -----------------------------
# 6. Sleep vs Mood
# -----------------------------
plt.figure(figsize=(6,5))
sns.scatterplot(x=df["sleep_hours"], y=df["mood_score"])
plt.title("Sleep Hours vs Mood")
plt.tight_layout()
plt.savefig(f"{plot_dir}/sleep_vs_mood.png")
plt.close()

print("All plots saved in /plots folder")