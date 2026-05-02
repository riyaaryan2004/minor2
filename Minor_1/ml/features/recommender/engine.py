from .fetcher import fetch_movie_pool
from .ranking import rank_movies
from .profile import add_to_history
from .cache import get_today_cache, set_today_cache
from .config import decide_genres

from ml.features.predict_day import predict_day


def recommend_movies(row):

    # 🔥 Predict mood & productivity
    result = predict_day(row)
    mood = result["mood"]
    prod = result["productivity"]

    print("\n--- Movie Recommendation Engine ---")
    print(f"Mood: {round(mood,2)} | Productivity: {round(prod,2)}")

    # 🎯 Decide genres using ML
    genres = decide_genres(mood, prod)
    print("Selected genres:", genres)

    # 🔥 Cache (based only on mood+prod)
    cached = get_today_cache(genres)
    if cached:
        print("✅ Using cached recommendations")
        return cached

    # 🎬 Fetch large pool
    pool = fetch_movie_pool(genres)

    if not pool:
        print("⚠️ No movies fetched, using fallback")
        return [
            {"title": "Inception", "vote_average": 8.8},
            {"title": "Interstellar", "vote_average": 8.6},
            {"title": "The Dark Knight", "vote_average": 9.0},
        ]

    print(f"📦 Pool size: {len(pool)}")

    # 🎯 Rank movies
    ranked = rank_movies(pool, mood, prod)

    # Return a broad set so the UI has enough Hindi and famous English picks.
    final = ranked[:30]

    print("🔥 Returning top:", len(final))

    # 🎯 Save history
    for m in final:
        add_to_history(m)

    # 💾 Cache results
    set_today_cache(genres, final)

    return final


# Debug run
if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv("ml/data/daily_data.csv")
    row = df.tail(1).iloc[0]

    movies = recommend_movies(row)

    print("\n🎬 Debug Output:\n")
    for m in movies:
        print(m.get("title"))
