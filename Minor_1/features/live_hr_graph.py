import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import sys

# BASE DIR (project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ACCESS TOKEN
ACCESS_TOKEN = sys.argv[1]

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# -----------------------------
# DATE INPUT (flexible)
# -----------------------------
if len(sys.argv) == 2:
    # default → today only
    start_date = datetime.now()
    end_date = datetime.now()

elif len(sys.argv) == 3:
    # single date
    start_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    end_date = start_date

elif len(sys.argv) == 4:
    # date range
    start_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    end_date = datetime.strptime(sys.argv[3], "%Y-%m-%d")

else:
    print("Usage:")
    print("1 day: python live_hr_graph.py <TOKEN> 2026-04-01")
    print("range: python live_hr_graph.py <TOKEN> 2026-04-01 2026-04-05")
    sys.exit()

# GRAPH DIRECTORY (inside features)
HR_GRAPH_DIR = os.path.join(os.path.dirname(__file__), "hr_graph")
os.makedirs(HR_GRAPH_DIR, exist_ok=True)

day = start_date

while day <= end_date:
    date_str = day.strftime("%Y-%m-%d")

    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date_str}/1d/1min.json"

    try:
        response = requests.get(url, headers=headers, timeout=10).json()
    except:
        day += timedelta(days=1)
        continue

    dataset = response.get("activities-heart-intraday", {}).get("dataset", [])

    if dataset:
        all_hr = [entry["value"] for entry in dataset]

        # minute index (0..1439)
        x = list(range(len(all_hr)))

        plt.figure(figsize=(12, 4))
        plt.plot(x, all_hr, linewidth=1)

        plt.title(f"Heart Rate on {date_str}")
        plt.xlabel("Hour of Day")
        plt.ylabel("Heart Rate (BPM)")

        # X axis → show hour marks only
        hour_ticks = list(range(0, 1440, 60))
        hour_labels = list(range(24))
        plt.xticks(hour_ticks, hour_labels)

        # Y axis safe range
        plt.ylim(40, 160)

        plt.grid(alpha=0.3)

        plt.tight_layout()

        # SAVE GRAPH (correct path)
        plt.savefig(os.path.join(HR_GRAPH_DIR, f"hr_{date_str}.png"))
        plt.close()

    day += timedelta(days=1)

print("All daily heart rate graphs saved in hr_graph folder.")