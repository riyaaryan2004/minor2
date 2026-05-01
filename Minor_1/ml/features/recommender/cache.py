import json
import os
import datetime

CACHE_FILE = "movie_cache.json"


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# 🔥 FIXED: stable cache key
def get_cache_key(user_filters, mood, prod):
    today = str(datetime.date.today())

    filters_str = json.dumps(user_filters, sort_keys=True)

    return f"{today}_{filters_str}_{round(mood,1)}_{round(prod,1)}"


def get_today_cache(user_filters, mood, prod):
    cache = load_cache()
    key = get_cache_key(user_filters, mood, prod)
    return cache.get(key)


def set_today_cache(user_filters, mood, prod, movies):
    cache = load_cache()
    key = get_cache_key(user_filters, mood, prod)
    cache[key] = movies
    save_cache(cache)


def clear_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)