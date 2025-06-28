import sqlite3
import os

DB_PATH = os.path.abspath("../db/FleetStat.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Vehicle table
c.execute("""
CREATE TABLE IF NOT EXISTS vehicle_info (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_name TEXT,
    vehicle_number TEXT UNIQUE,
    owner_name TEXT,
    vehicle_type TEXT,
    registration_date TEXT
)
""")

# Trip table
c.execute("""
CREATE TABLE IF NOT EXISTS trip_info (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_number TEXT,
    fuel_consumption REAL,
    trip_date TEXT,
    start_location TEXT,
    end_location TEXT,
    lat_start REAL,
    lon_start REAL,
    lat_end REAL,
    lon_end REAL,
    distance REAL
)
""")

conn.commit()
conn.close()
print("✅ Database tables created successfully.")
