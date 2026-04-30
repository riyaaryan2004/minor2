import requests

def fetch_data(url, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {}

    return res.json()