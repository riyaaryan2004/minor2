import requests
import sys
import os
import random

API_KEY = "6439995846ae6446d2e2e4079a88f34a"


# -------------------------------
# 1. IMPORT YOUR ML OUTPUT
# -------------------------------
def get_today_scores():
    import io

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(base_dir)

    from predict_day import predict_day

    current_dir = os.getcwd()
    os.chdir(base_dir)

    # 🔇 Suppress prints
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        mood_score, prod_score = predict_day()
    finally:
        sys.stdout = old_stdout
        os.chdir(current_dir)

    return mood_score, prod_score


# -------------------------------
# 2. LABELS
# -------------------------------
def mood_label(score):
    score = round(score)
    mapping = {
        1:"Extremely bad",
        2:"Very low",
        3:"Low",
        4:"Slightly low",
        5:"Neutral",
        6:"Decent",
        7:"Good",
        8:"Very good",
        9:"Great",
        10:"Excellent"
    }
    return mapping.get(score, "Unknown")


def prod_label(score):
    score = round(score)
    mapping = {
        1:"Extremely low",
        2:"Very low",
        3:"Low",
        4:"Below average",
        5:"Average",
        6:"Above average",
        7:"Good",
        8:"Very productive",
        9:"Highly productive",
        10:"Peak productivity"
    }
    return mapping.get(score, "Unknown")


# -------------------------------
# 3. STATE ANALYSIS
# -------------------------------
def analyze_state(mood, prod):
    if mood <= 2:
        mood_state = "very_low"
    elif mood <= 3.5:
        mood_state = "low"
    elif mood <= 5.5:
        mood_state = "neutral"
    elif mood <= 7.5:
        mood_state = "good"
    else:
        mood_state = "excellent"

    if prod <= 3:
        prod_state = "low"
    elif prod <= 6:
        prod_state = "medium"
    else:
        prod_state = "high"

    return mood_state, prod_state


# -------------------------------
# 4. INSIGHT
# -------------------------------
def combined_insight(mood, prod):
    if mood < 4 and prod < 4:
        return "Low energy day — you may need rest and light content."
    elif mood < 4 and prod >= 6:
        return "Pushing through low mood — emotional content may resonate."
    elif mood >= 6 and prod < 4:
        return "Good mood but low drive — light entertainment fits."
    elif mood >= 6 and prod >= 6:
        return "High energy state — intense and engaging content suits you."
    else:
        return "Balanced state — flexible viewing options."


# -------------------------------
# 5. GENRE DECISION
# -------------------------------
def decide_genre(mood_state, prod_state):

    GENRES = {
        "action": 28,
        "comedy": 35,
        "drama": 18,
        "romance": 10749,
        "animation": 16,
        "thriller": 53
    }

    if mood_state in ["very_low", "low"]:
        if prod_state == "low":
            return GENRES["animation"], "comfort + easy watch"
        elif prod_state == "medium":
            return GENRES["comedy"], "light mood lifting"
        else:
            return GENRES["drama"], "emotional engagement"

    elif mood_state == "neutral":
        if prod_state == "low":
            return GENRES["romance"], "relaxing"
        elif prod_state == "medium":
            return GENRES["comedy"], "balanced fun"
        else:
            return GENRES["thriller"], "engaging"

    elif mood_state in ["good", "excellent"]:
        if prod_state == "low":
            return GENRES["comedy"], "fun + chill"
        elif prod_state == "medium":
            return GENRES["action"], "energetic"
        else:
            return GENRES["thriller"], "high focus + intensity"

    return GENRES["comedy"], "default"


# -------------------------------
# 6. LANGUAGE DECISION
# -------------------------------
def decide_languages(mood, prod):
    if mood < 4:
        return ["hi", "en"]   # comfort → Hindi + English
    elif mood >= 7 and prod >= 6:
        return ["en"]         # intense → English
    else:
        return ["hi", "en"]   # mixed


# -------------------------------
# 7. FETCH MOVIES
# -------------------------------
def fetch_movies(genre_id, language):
    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": API_KEY,
        "with_original_language": language,
        "sort_by": "popularity.desc",
        "with_genres": genre_id,
        "vote_average.gte": 7.0,
        "vote_count.gte": 300,
        "release_date.gte": "2005-01-01",
        "release_date.lte": "2023-12-31",
        "include_adult": False,
        "page": 1
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        return []

    data = response.json()
    results = data.get("results", [])

    random.shuffle(results)  # add variation
    return results[:5]


# -------------------------------
# 8. MAIN PIPELINE
# -------------------------------
def recommend_movies():
    mood, prod = get_today_scores()

    print("\n--- Movie Recommendation Engine ---")

    print(f"\nMood Score: {round(mood,2)} ({mood_label(mood)})")
    print(f"Productivity Score: {round(prod,2)} ({prod_label(prod)})")

    print("Insight:", combined_insight(mood, prod))

    mood_state, prod_state = analyze_state(mood, prod)

    print(f"\nDetected Mood State: {mood_state}")
    print(f"Detected Productivity State: {prod_state}")

    genre_id, logic = decide_genre(mood_state, prod_state)

    print(f"Strategy: {logic}")

    languages = decide_languages(mood, prod)
    print(f"Language Preference: {', '.join(languages)}")

    movies = []

    for lang in languages:
        movies.extend(fetch_movies(genre_id, lang))

    # remove duplicates
    seen = set()
    unique_movies = []
    for m in movies:
        if m["title"] not in seen:
            unique_movies.append(m)
            seen.add(m["title"])

    unique_movies = unique_movies[:5]

    print("\n🎬 Recommended Movies:\n")

    if not unique_movies:
        print("No movies found.")
        return

    for i, movie in enumerate(unique_movies, 1):
        year = movie.get("release_date", "N/A")[:4] if movie.get("release_date") else "N/A"
        print(f"{i}. {movie['title']} ({year}) ⭐ {movie['vote_average']}")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    recommend_movies()