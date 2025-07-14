import sqlite3
import random
from datetime import datetime, timedelta

# Connect to your database
conn = sqlite3.connect('../db/FleetStat.db')
c = conn.cursor()

vehicle_numbers = ["ABC123", "XYZ789", "LMN456", "PQR678", "DEF234"]

# Function to generate random GPS coords near a base location (latitude, longitude)
def random_coords(base_lat, base_lon, delta=0.5):
    return round(base_lat + random.uniform(-delta, delta), 6), round(base_lon + random.uniform(-delta, delta), 6)

# Function to generate synthetic trip data
def generate_trip(vehicle_number, start_date):
    # Random trip distance between 5 km and 500 km
    distance = round(random.uniform(5, 500), 1)
    # Fuel consumption roughly 0.06 to 0.15 liters per km plus some noise
    fuel_consumption = round(distance * random.uniform(0.06, 0.15), 2)

    # Random start location coords near some city centers (using Delhi as base)
    lat_start, lon_start = random_coords(28.7041, 77.1025)
    # End location offset by some distance (simulate realistic lat/lon difference)
    lat_end, lon_end = random_coords(lat_start, lon_start, delta=1.5)

    # Fake start and end location names
    start_location = f"Loc_{random.randint(1, 100)}"
    end_location = f"Loc_{random.randint(101, 200)}"

    # Random trip date between start_date and today
    trip_date = start_date + timedelta(days=random.randint(0, 60))

    return (vehicle_number, fuel_consumption, trip_date.strftime('%Y-%m-%d'), start_location, end_location,
            lat_start, lon_start, lat_end, lon_end, distance)

# Generate and insert 200 synthetic trips
start_date = datetime(2025, 5, 1)
num_trips = 200

for _ in range(num_trips):
    vehicle = random.choice(vehicle_numbers)
    trip = generate_trip(vehicle, start_date)

    c.execute('''
        INSERT INTO trip_info (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                               lat_start, lon_start, lat_end, lon_end, distance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', trip)

conn.commit()
conn.close()

print(f"Inserted {num_trips} synthetic trips into the database!")
