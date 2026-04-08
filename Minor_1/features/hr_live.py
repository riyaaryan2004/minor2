import requests

def get_intraday_hr(access_token, date):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"

    response = requests.get(url, headers=headers).json()

    dataset = response.get("activities-heart-intraday", {}).get("dataset", [])

    result = []

    for i, entry in enumerate(dataset):
        result.append({
            "time": entry["time"],   # "00:01"
            "hr": entry["value"]
        })
    #print(response)
    return result