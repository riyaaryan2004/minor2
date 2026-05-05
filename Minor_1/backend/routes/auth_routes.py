from flask import Blueprint, redirect, request
import requests, base64
from backend.config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from backend.services.token_service import save_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    url = (
        "https://www.fitbit.com/oauth2/authorize"
        f"?response_type=code&client_id={CLIENT_ID}"
        "&scope=heartrate activity sleep"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(url)

@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return {"error": "No authorization code"}, 400

    token_url = "https://api.fitbit.com/oauth2/token"

    auth_header = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    res = requests.post(token_url, headers=headers, data=data)

    if res.status_code != 200:
        return {"error": "Token exchange failed"}, 400

    token = res.json().get("access_token")

    if not token:
        return {"error": "No access token received"}, 400

    save_token(token)

    return redirect("/")   