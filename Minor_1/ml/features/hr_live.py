import requests

def get_intraday_hr_response(access_token, date):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"

    response = requests.get(url, headers=headers, timeout=20)
    data = response.json()

    dataset = data.get("activities-heart-intraday", {}).get("dataset", [])
    result = []

    for entry in dataset:
        result.append({
            "time": entry["time"],
            "hr": entry["value"]
        })

    return {
        "statusCode": response.status_code,
        "data": result,
        "errors": data.get("errors", []),
    }


def get_intraday_hr(access_token, date):
    return get_intraday_hr_response(access_token, date)["data"]
