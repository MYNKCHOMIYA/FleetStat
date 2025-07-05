import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../db/FleetStat.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

def insert_vehicle(vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date):
    c.execute('''
        INSERT INTO vehicle_info (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date))
    conn.commit()

def insert_trip(vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                lat_start, lon_start, lat_end, lon_end, distance):
    c.execute('''
        INSERT INTO trip_info (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                               lat_start, lon_start, lat_end, lon_end, distance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
          lat_start, lon_start, lat_end, lon_end, distance))
    conn.commit()

def view_vehicles():
    c.execute('SELECT * FROM vehicle_info')
    return c.fetchall()

def view_trips():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trip_info ORDER BY trip_date DESC", conn)
    conn.close()
    return df
