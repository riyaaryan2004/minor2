import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import sys

# Take access token from command argument
ACCESS_TOKEN = sys.argv[1]

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

start_date = datetime(2026, 3, 1)
end_date = datetime.now()

# Create folder if it doesn't exist
os.makedirs("hr_graph", exist_ok=True)

day = start_date

while day <= end_date:
    date_str = day.strftime("%Y-%m-%d")
    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date_str}/1d/1min.json"
    
    response = requests.get(url, headers=headers).json()
    dataset = response.get("activities-heart-intraday", {}).get("dataset", [])

    if dataset:
        all_hr = [entry["value"] for entry in dataset]

        # minute index (0..1439)
        x = list(range(len(all_hr)))

        plt.figure(figsize=(12,4))

        plt.plot(x, all_hr, linewidth=1)

        plt.title(f"Heart Rate on {date_str}")
        plt.xlabel("Hour of Day")
        plt.ylabel("Heart Rate (BPM)")

        # X axis → show hour marks only
        hour_ticks = list(range(0, 1440, 60))
        hour_labels = list(range(24))

        plt.xticks(hour_ticks, hour_labels)

        # Expand Y axis slightly
        ymin = min(all_hr) - 5
        ymax = max(all_hr) + 5
        plt.ylim(40, 160)

        plt.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"hr_graph/hr_{date_str}.png")
        plt.close()
        
    day += timedelta(days=1)

print("All daily heart rate graphs saved in hr_graph folder.")