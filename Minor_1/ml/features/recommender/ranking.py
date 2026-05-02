from .profile import load_profile


HINDI_TITLES = {
    "3 idiots",
    "dangal",
    "zindagi na milegi dobara",
    "queen",
    "taare zameen par",
    "chak de! india",
    "lagaan",
    "barfi!",
    "wake up sid",
    "dil chahta hai",
    "yeh jawaani hai deewani",
    "bajrangi bhaijaan",
    "pk",
    "swades",
}


FAMOUS_TITLES = HINDI_TITLES | {
    "inception",
    "interstellar",
    "the dark knight",
    "the shawshank redemption",
    "forrest gump",
    "the pursuit of happyness",
    "la la land",
    "the social network",
    "the prestige",
    "catch me if you can",
}


def score_movie(movie, mood, prod, profile):
    score = 0

    vote_average = movie.get("vote_average") or 0
    vote_count = movie.get("vote_count") or 0
    popularity = movie.get("popularity") or 0
    genres = movie.get("genre_ids", [])
    title = movie.get("title", "")
    title_key = title.lower().strip()
    language = movie.get("original_language", "")

    # Strong base quality, with vote count/popularity favoring known movies.
    score += vote_average * 2.5
    score += min(vote_count, 3000) / 300
    score += min(popularity, 100) * 0.08

    # Prefer Hindi/Bollywood, while still allowing famous Hollywood.
    if language == "hi":
        score += 8
    if title_key in HINDI_TITLES:
        score += 10
    elif title_key in FAMOUS_TITLES:
        score += 5

    # Mood alignment.
    if mood < 4:
        if 35 in genres:
            score += 7
        if 10749 in genres:
            score += 4
        if 10751 in genres:
            score += 3
    elif mood < 7:
        if 18 in genres:
            score += 6
        if 35 in genres:
            score += 3
        if 9648 in genres:
            score += 3
    else:
        if 28 in genres:
            score += 6
        if 12 in genres:
            score += 4
        if 53 in genres:
            score += 4

    # Productivity alignment.
    if prod < 4:
        if 35 in genres or 10751 in genres:
            score += 4
    elif prod > 7:
        if 28 in genres or 53 in genres or 12 in genres:
            score += 4
    else:
        if 18 in genres or 9648 in genres:
            score += 3

    liked = set(profile.get("liked", []))
    disliked = set(profile.get("disliked", []))
    history = set(profile.get("history", []))

    if title in liked:
        score += 8
    if title in disliked:
        score -= 25
    if title in history:
        score -= 3

    return score


def rank_movies(movies, mood, prod):
    profile = load_profile()

    return sorted(
        movies,
        key=lambda movie: score_movie(movie, mood, prod, profile),
        reverse=True,
    )
