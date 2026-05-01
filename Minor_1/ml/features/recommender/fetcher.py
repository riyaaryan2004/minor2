import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_KEY = "6439995846ae6446d2e2e4079a88f34a"


def fetch_movies(genre_ids, user_filters=None):
    user_filters = user_filters or {}   # 🔥 safety

    url = "https://api.themoviedb.org/3/discover/movie"

    # 🔥 base params
    params = {
        "api_key": API_KEY,
        "with_genres": ",".join(map(str, genre_ids)),
        "sort_by": "popularity.desc",
        "include_adult": False,
        "page": 1,
        "vote_average.gte": user_filters.get("min_rating", 6.5),
        "vote_count.gte": 100,
    }

    # 🔥 filters
    if user_filters.get("language"):
        params["with_original_language"] = user_filters["language"]

    if user_filters.get("year_after"):
        params["primary_release_date.gte"] = f"{user_filters['year_after']}-01-01"

    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1)
    session.mount("https://", HTTPAdapter(max_retries=retry))

    try:
        # 🔥 Attempt 1 (strict)
        res = session.get(url, params=params, timeout=10)
        data = res.json()
        results = data.get("results", [])

        if results:
            return results[:20]

        print("⚠️ No results (strict), relaxing filters...")

        # 🔥 Attempt 2 (remove vote_count)
        params.pop("vote_count.gte", None)
        res = session.get(url, params=params, timeout=10)
        data = res.json()
        results = data.get("results", [])

        if results:
            return results[:20]

        print("⚠️ No results (relaxed), removing language...")

        # 🔥 Attempt 3 (remove language)
        params.pop("with_original_language", None)
        res = session.get(url, params=params, timeout=10)
        data = res.json()
        results = data.get("results", [])

        if results:
            return results[:20]

        print("⚠️ No results at all → returning empty")
        return []

    except Exception as e:
        print("Fetch error:", e)
        return []