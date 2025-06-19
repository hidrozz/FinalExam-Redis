import csv
from datetime import datetime

def log_latency(platform, published, received, stored, read):
    filename = f"latency_{platform.lower()}.csv"
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), published, received, stored, read])
