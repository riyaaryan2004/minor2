# scoring logic
from .profile import load_profile

def score_movie(movie, mood, prod, profile):
    score = 0

    # base rating
    score += movie.get("vote_average", 0) * 2

    # popularity
    score += movie.get("popularity", 0) * 0.01

    # mood alignment
    genres = movie.get("genre_ids", [])

    if mood < 4 and 35 in genres:  # comedy
        score += 5

    if mood >= 7 and 53 in genres:  # thriller
        score += 5

    # user preferences
    title = movie.get("title", "")

    return score


def rank_movies(movies, mood, prod):
    profile = load_profile()

    return sorted(
        movies,
        key=lambda m: score_movie(m, mood, prod, profile),
        reverse=True
    )