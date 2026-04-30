from backend.config import TOKEN_FILE

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def get_token():
    try:
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    except:
        return None