# main pipeline (entry point)

from .fetcher import fetch_movies
from .ranking import rank_movies
from .profile import add_to_history
from .cache import get_today_cache, set_today_cache
from .config import decide_genre
from ml.features.predict_day import predict_day


def recommend_movies(row, user_filters=None):

    user_filters = user_filters or {}   # 🔥 safety fix

    result = predict_day(row)

    if isinstance(result, tuple):
        mood, prod = result
    else:
        mood = result["mood"]
        prod = result["productivity"]

    print("\n--- Movie Recommendation Engine ---")
    print(f"Mood: {round(mood,2)} | Productivity: {round(prod,2)}")

    # 🔥 cache with filters
    cached = get_today_cache(user_filters, mood, prod)
    if cached:
        print("Using cached recommendations")
        return cached

    # 🔥 user genre override
    if user_filters.get("genre"):
        genres = [user_filters["genre"]]
        print("Using USER genre:", genres)
    else:
        genres = decide_genre(mood, prod)
        print("Selected genres (ML):", genres)

    movies = fetch_movies(genres, user_filters)

    if not movies:
        print("⚠️ No movies found, trying fallback...")

        # fallback 1: remove filters
        movies = fetch_movies(genres, {})

        # fallback 2: switch genre
        if not movies:
            movies = fetch_movies([28], {})  # action fallback

        # fallback 3: final safety
        if not movies:
            return [
                {"title": "Inception", "vote_average": 8.8},
                {"title": "Interstellar", "vote_average": 8.6},
                {"title": "The Dark Knight", "vote_average": 9.0},
            ]

    ranked = rank_movies(movies, mood, prod)
    final = ranked[:5]

    print("Genres:", genres)
    print("Filters:", user_filters)
    print("Fetched count:", len(movies))

    for m in final:
        add_to_history(m)

    if final:
        set_today_cache(user_filters, mood, prod, final)

    return final


if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv("ml/data/daily_data.csv")
    row = df.tail(1).iloc[0]

    movies = recommend_movies(row)

    print("\n🎬 Debug Output:\n")
    for m in movies:
        print(m["title"])