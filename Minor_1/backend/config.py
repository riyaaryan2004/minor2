import os

# backend/
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# project root (Minor_1)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# ml folder
ML_DIR = os.path.join(PROJECT_ROOT, "ml")

# data + models
DATA_DIR = os.path.join(ML_DIR, "data")
MODEL_DIR = os.path.join(ML_DIR, "saved_models")

# token
TOKEN_FILE = os.path.join(BASE_DIR, "token.txt")
CLIENT_ID = "23TXMK"
CLIENT_SECRET = "b19bed40782c38915f7a78687262612b"
REDIRECT_URI = "http://localhost:5000/callback"