import sqlite3
import os
import sqlite3

# Resolve absolute path to ../db/FleetStat.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../db/FleetStat.db")

# Connect to SQLite
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()


# Insert vehicle data
def insert_vehicle(vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date):
    c.execute('''
        INSERT INTO vehicle_info (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date))
    conn.commit()

# Insert trip data
def insert_trip(vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                lat_start, lon_start, lat_end, lon_end, distance):
    c.execute('''
        INSERT INTO trip_info (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                               lat_start, lon_start, lat_end, lon_end, distance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
          lat_start, lon_start, lat_end, lon_end, distance))
    conn.commit()

# Fetch all vehicles
def view_vehicles():
    c.execute('SELECT * FROM vehicle_info')
    return c.fetchall()

# Fetch all trips
def view_trips():
    c.execute('SELECT * FROM trip_info')
    return c.fetchall()
