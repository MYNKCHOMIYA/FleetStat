import sqlite3
import os

# Connect to the SQLite database
conn = sqlite3.connect(r"C:\Users\MAYANK\Desktop\FleetStat\db\FleetStat.db")

# Create tables
def create_table():
    c = conn.cursor()

    # vehicle_info table
    c.execute('''CREATE TABLE IF NOT EXISTS vehicle_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_name TEXT NOT NULL,
        vehicle_number TEXT NOT NULL UNIQUE,
        owner_name TEXT NOT NULL,
        vehicle_type TEXT NOT NULL,
        registration_date TEXT NOT NULL
    )''')

    # trip_info table
    c.execute('''CREATE TABLE IF NOT EXISTS trip_info (
        trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT NOT NULL,
        fuel_consumption REAL NOT NULL,
        trip_date TEXT NOT NULL,
        start_location TEXT NOT NULL,
        end_location TEXT NOT NULL,
        lat_start REAL NOT NULL,
        lon_start REAL NOT NULL,
        lat_end REAL NOT NULL,
        lon_end REAL NOT NULL,
        distance REAL NOT NULL,
        FOREIGN KEY (vehicle_number) REFERENCES vehicle_info(vehicle_number)
    )''')

    conn.commit()
    c.close()

# Insert into vehicle_info
def insert_vehicle_info(vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date):
    c = conn.cursor()
    c.execute('''INSERT INTO vehicle_info (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date)
                 VALUES (?, ?, ?, ?, ?)''',
              (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date))
    conn.commit()
    c.close()

# Insert into trip_info (trip_id is auto-generated)
def insert_trip_info(vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                     lat_start, lon_start, lat_end, lon_end, distance):
    c = conn.cursor()
    c.execute('''INSERT INTO trip_info (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                 lat_start, lon_start, lat_end, lon_end, distance)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
               lat_start, lon_start, lat_end, lon_end, distance))
    conn.commit()
    c.close()

# Fetch all vehicles
def get_all_vehicles():
    c = conn.cursor()
    c.execute('SELECT * FROM vehicle_info')
    vehicles = c.fetchall()
    c.close()
    return vehicles

# Fetch all trips
def get_all_trips():
    c = conn.cursor()
    c.execute('SELECT * FROM trip_info')
    trips = c.fetchall()
    c.close()
    return trips

# Run table creation
if __name__ == '__main__':
    create_table()
    print("Database and tables created successfully.")

