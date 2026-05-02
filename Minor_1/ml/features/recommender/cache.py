import json
import os
import datetime

CACHE_FILE = "movie_cache.json"
CACHE_VERSION = "v2"


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# 🔑 Stable key (NO mood randomness)
def get_cache_key(genres):
    today = str(datetime.date.today())
    genres_str = ",".join(map(str, sorted(genres)))
    return f"{CACHE_VERSION}_{today}_{genres_str}"


def get_today_cache(genres):
    cache = load_cache()
    return cache.get(get_cache_key(genres))


def set_today_cache(genres, pool):
    # 🔥 remove bad/incomplete movies before caching
    clean_pool = [m for m in pool if m.get("id")]

    cache = load_cache()
    cache[get_cache_key(genres)] = clean_pool
    save_cache(cache)


def clear_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
