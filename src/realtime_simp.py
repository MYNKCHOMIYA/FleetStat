import time
from db_handler import insert_trip
from datetime import datetime
from random import uniform

def simulate_trip():
    while True:
        insert_trip(
            vehicle_number="RJ14XYZ1234",
            fuel_consumption=round(uniform(2.5, 8.5), 2),
            trip_date=datetime.now().date(),
            start_location="Jaipur",
            end_location="Churu",
            lat_start=26.9124, lon_start=75.7873,
            lat_end=28.3042, lon_end=74.7375,
            distance=round(uniform(180, 220), 2)
        )
        print("Trip inserted.")
        time.sleep(5)  # Simulate every 5 seconds

if __name__ == "__main__":
    simulate_trip()
