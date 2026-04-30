import os
import csv

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def read_csv_dict(file_path):
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv_dict(file_path, fieldnames, rows):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)