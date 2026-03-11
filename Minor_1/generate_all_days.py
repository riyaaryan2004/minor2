import subprocess
from datetime import datetime, timedelta
import sys

SCRIPT_NAME = "repair_day.py"

if len(sys.argv) < 2:
    print("Usage: python generate_all_days.py ACCESS_TOKEN")
    exit()

token = sys.argv[1]

start_date = datetime(2026,3,1)
end_date = datetime.now()

current = start_date

while current <= end_date:

    date_str = current.strftime("%Y-%m-%d")

    print("Generating:", date_str)

    subprocess.run([
        "python",
        SCRIPT_NAME,
        date_str,
        token
    ])

    current += timedelta(days=1)

print("All days generated successfully")