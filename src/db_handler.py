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

def Update_vehicle(vehicle_id, vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date):
    c.execute('''
        UPDATE vehicle_info
        SET vehicle_name = ?, vehicle_number = ?, owner_name = ?, vehicle_type = ?, registration_date = ?
        WHERE vehicle_id = ?
    ''', (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date, vehicle_id))
    conn.commit()

def Update_trip(trip_id, vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                lat_start, lon_start, lat_end, lon_end, distance):
    c.execute('''
        UPDATE trip_info
        SET vehicle_number = ?, fuel_consumption = ?, trip_date = ?, start_location = ?, end_location = ?,
            lat_start = ?, lon_start = ?, lat_end = ?, lon_end = ?, distance = ?
        WHERE trip_id = ?
    ''', (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
          lat_start, lon_start, lat_end, lon_end, distance, trip_id))
    conn.commit()

def delete_vehicle(vehicle_id):
    c.execute('DELETE FROM vehicle_info WHERE vehicle_id = ?', (vehicle_id,))
    conn.commit()
    
def delete_trip(trip_id):
    c.execute('DELETE FROM trip_info WHERE trip_id = ?', (trip_id,))
    conn.commit()

def view_vehicles():
    c.execute('SELECT * FROM vehicle_info')
    return c.fetchall()

def view_trips():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trip_info ORDER BY trip_date DESC", conn)
    conn.close()
    return df
