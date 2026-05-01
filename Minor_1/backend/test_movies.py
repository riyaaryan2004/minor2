import sys
import os

# 🔥 MUST COME FIRST
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# now imports will work
from ml.features.recommender.engine import recommend_movies
import pandas as pd

# path
DATA_PATH = os.path.join("ml", "data", "daily_data.csv")

df = pd.read_csv(DATA_PATH)

if df.empty:
    print("No data found")
else:
    row = df.tail(1).iloc[0]

    movies = recommend_movies(row)

    print("\n🎬 Recommended Movies:\n")

    for i, m in enumerate(movies, 1):
        print(f"{i}. {m['title']} ⭐ {m.get('vote_average', 'N/A')}")