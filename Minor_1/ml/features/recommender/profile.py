import json
import os

PROFILE_FILE = "user_profile.json"
MAX_HISTORY = 30


def load_profile():
    if not os.path.exists(PROFILE_FILE):
        return {"liked": [], "disliked": [], "history": []}

    try:
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"liked": [], "disliked": [], "history": []}


def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)


# ===============================
# 🎬 ADD TO HISTORY (CONTROLLED)
# ===============================
def add_to_history(movie):
    profile = load_profile()

    title = movie.get("title")

    if not title:
        return

    if title in profile["history"]:
        return

    profile["history"].append(title)

    # 🔥 limit history size
    if len(profile["history"]) > MAX_HISTORY:
        profile["history"] = profile["history"][-MAX_HISTORY:]

    save_profile(profile)


# ===============================
# ❤️ LIKE MOVIE
# ===============================
def like_movie(title):
    profile = load_profile()

    if title not in profile["liked"]:
        profile["liked"].append(title)

    # remove from disliked if present
    if title in profile["disliked"]:
        profile["disliked"].remove(title)

    save_profile(profile)


# ===============================
# 👎 DISLIKE MOVIE
# ===============================
def dislike_movie(title):
    profile = load_profile()

    if title not in profile["disliked"]:
        profile["disliked"].append(title)

    # remove from liked if present
    if title in profile["liked"]:
        profile["liked"].remove(title)

    save_profile(profile)


# ===============================
# 🚫 FILTER OUT SEEN/DISLIKED
# ===============================
def filter_seen_movies(movies):
    profile = load_profile()

    seen = set(profile["history"])
    disliked = set(profile["disliked"])

    filtered = []

    for m in movies:
        title = m.get("title")

        if title in seen:
            continue

        if title in disliked:
            continue

        filtered.append(m)

    return filtered