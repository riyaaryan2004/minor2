import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_KEY = "6439995846ae6446d2e2e4079a88f34a"
URL = "https://api.themoviedb.org/3/discover/movie"
MIN_VOTE_COUNT = 80
MAX_POOL_SIZE = 90


def filter_safe_movies(movies):
    safe = []

    for movie in movies:
        if movie.get("adult"):
            continue
        if not movie.get("poster_path"):
            continue
        if (movie.get("vote_count") or 0) < MIN_VOTE_COUNT:
            continue
        if (movie.get("popularity") or 0) < 2:
            continue

        safe.append(movie)

    return safe


def build_fallback():
    fallback_data = [
        ("3 Idiots", 8.4, "hi", [35, 18], "College life, friendship, and pressure handled with warmth."),
        ("Dangal", 8.3, "hi", [18, 28], "An inspiring sports drama about family and ambition."),
        ("Zindagi Na Milegi Dobara", 7.6, "hi", [35, 18, 10749], "A feel-good road trip about friendship and rediscovery."),
        ("Queen", 7.4, "hi", [35, 18], "A gentle, uplifting story of independence."),
        ("Taare Zameen Par", 8.3, "hi", [18, 10751], "A moving story about empathy, learning, and childhood."),
        ("Chak De! India", 7.8, "hi", [18], "A motivational sports drama."),
        ("Lagaan", 7.3, "hi", [12, 18], "A beloved period sports drama."),
        ("Barfi!", 7.6, "hi", [35, 18, 10749], "A warm romantic comedy-drama."),
        ("Wake Up Sid", 7.2, "hi", [35, 18, 10749], "A coming-of-age comfort watch."),
        ("Dil Chahta Hai", 7.1, "hi", [35, 18, 10749], "A classic friendship drama."),
        ("Yeh Jawaani Hai Deewani", 7.2, "hi", [35, 18, 10749], "A popular romantic travel drama."),
        ("Bajrangi Bhaijaan", 7.8, "hi", [35, 18, 28], "A heartfelt crowd-pleaser."),
        ("PK", 7.7, "hi", [35, 18], "A famous satirical comedy-drama."),
        ("Swades", 7.4, "hi", [18], "A thoughtful drama about purpose and home."),
        ("Inception", 8.8, "en", [28, 53], "A mind-bending thriller."),
        ("Interstellar", 8.6, "en", [12, 18], "A journey through space and time."),
        ("The Dark Knight", 9.0, "en", [28, 80, 18], "Batman faces Joker."),
        ("Forrest Gump", 8.5, "en", [35, 18, 10749], "A famous emotional classic."),
        ("The Pursuit of Happyness", 8.0, "en", [18], "An uplifting perseverance story."),
        ("La La Land", 7.9, "en", [35, 18, 10749], "A stylish romantic musical drama."),
        ("The Social Network", 7.7, "en", [18], "A sharp modern drama."),
        ("The Prestige", 8.2, "en", [18, 9648, 53], "A clever mystery thriller."),
        ("Catch Me If You Can", 8.0, "en", [18, 80], "A breezy famous crime drama."),
        ("The Shawshank Redemption", 8.7, "en", [18], "A timeless hope-filled drama."),
    ]

    return [
        {
            "id": 10001 + index,
            "title": title,
            "poster_path": "",
            "vote_average": rating,
            "vote_count": 1000,
            "popularity": 40,
            "original_language": language,
            "genre_ids": genres,
            "overview": overview,
        }
        for index, (title, rating, language, genres, overview) in enumerate(fallback_data)
    ]


def build_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def discover_movies(session, genre_ids, language, pages):
    params = {
        "api_key": API_KEY,
        "with_genres": "|".join(map(str, genre_ids)),
        "with_original_language": language,
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "region": "IN",
        "watch_region": "IN",
        "certification_country": "IN",
        "certification.lte": "UA",
        "vote_count.gte": MIN_VOTE_COUNT,
    }

    movies = []
    for page in range(1, pages + 1):
        page_params = params.copy()
        page_params["page"] = page

        response = session.get(URL, params=page_params, timeout=10)
        if response.status_code != 200:
            continue

        movies.extend(filter_safe_movies(response.json().get("results", [])))

    return movies


def fetch_movie_pool(genre_ids):
    try:
        session = build_session()

        hindi_pool = discover_movies(session, genre_ids, "hi", pages=6)
        english_pool = discover_movies(session, genre_ids, "en", pages=4)
        pool = hindi_pool + english_pool

        final_pool = list({movie["id"]: movie for movie in pool}.values())

        if len(final_pool) < 20:
            print("Weak TMDB pool, adding known fallback movies")
            final_pool.extend(build_fallback())
            final_pool = list({movie["id"]: movie for movie in final_pool}.values())

        print(f"Movie pool built: {len(final_pool)}")
        return final_pool[:MAX_POOL_SIZE]

    except Exception as exc:
        print("Fetch error:", exc)
        return build_fallback()
