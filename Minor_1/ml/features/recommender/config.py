# constants (genres,mapping)
GENRES = {
    "action": 28,
    "comedy": 35,
    "drama": 18,
    "romance": 10749,
    "animation": 16,
    "thriller": 53
}

def decide_genre(mood, prod):
    if mood < 4:
        return [GENRES["comedy"], GENRES["drama"]]
    elif mood >= 7 and prod >= 6:
        return [GENRES["action"], GENRES["thriller"]]
    elif mood >= 7:
        return [GENRES["romance"], GENRES["animation"]]
    else:
        return [GENRES["romance"], GENRES["comedy"]]