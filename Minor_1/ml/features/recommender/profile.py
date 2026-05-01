# user history + likes
import json
import os

PROFILE_FILE = "user_profile.json"

def load_profile():
    if not os.path.exists(PROFILE_FILE):
        return {"liked": [], "disliked": [], "history": []}

    with open(PROFILE_FILE, "r") as f:
        return json.load(f)


def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)


def add_to_history(movie):
    profile = load_profile()

    if movie["title"] not in profile["history"]:
        profile["history"].append(movie["title"])

    save_profile(profile)


def like_movie(title):
    profile = load_profile()
    if title not in profile["liked"]:
        profile["liked"].append(title)
    save_profile(profile)


def dislike_movie(title):
    profile = load_profile()
    if title not in profile["disliked"]:
        profile["disliked"].append(title)
    save_profile(profile)