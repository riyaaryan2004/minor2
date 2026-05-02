import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

GENRES = {
    "action": 28,
    "comedy": 35,
    "drama": 18,
    "romance": 10749,
    "animation": 16,
    "thriller": 53,
    "adventure": 12,
    "family": 10751,
    "fantasy": 14,
    "mystery": 9648
}

MOOD_BUCKETS = {
    "low": (0, 5),
    "medium": (5, 7),
    "high": (7, 10)
}

PROD_BUCKETS = {
    "low": (0, 5),
    "high": (5, 10)
}

GENRE_STRATEGY = {
    ("low", "low"): ["comedy", "romance"],
    ("low", "high"): ["comedy", "animation"],
    ("medium", "low"): ["family", "romance"],
    ("medium", "high"): ["drama", "mystery"],
    ("high", "low"): ["fantasy", "family"],
    ("high", "high"): ["action", "thriller"]
}


def get_bucket(value, buckets):
    for key, (low, high) in buckets.items():
        if low <= value < high:
            return key
    return "medium"


def decide_genres(mood, prod):
    mood_bucket = get_bucket(mood, MOOD_BUCKETS)
    prod_bucket = get_bucket(prod, PROD_BUCKETS)

    selected = GENRE_STRATEGY.get((mood_bucket, prod_bucket), ["comedy", "drama"])

    # 🔥 NO randomness → stable system
    return [GENRES[g] for g in selected]