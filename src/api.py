from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from db_handler import conn
import pandas as pd
import sqlite3

app = FastAPI(title="FleetStat API")

# ---------- Pydantic Models ----------
class Vehicle(BaseModel):
    vehicle_name: str
    vehicle_number: str
    owner_name: str
    vehicle_type: str
    registration_date: str

class Trip(BaseModel):
    vehicle_number: str
    fuel_consumption: float
    trip_date: str
    start_location: str
    end_location: str
    lat_start: float
    lon_start: float
    lat_end: float
    lon_end: float
    distance: float

# ---------- API Endpoints ----------

@app.get("/vehicles")
def get_vehicles():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicle_info")
    rows = cursor.fetchall()
    return rows

@app.post("/add_vehicle")
def add_vehicle(vehicle: Vehicle):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vehicle_info (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (vehicle.vehicle_name, vehicle.vehicle_number, vehicle.owner_name,
          vehicle.vehicle_type, vehicle.registration_date))
    conn.commit()
    return {"message": "✅ Vehicle added successfully"}

@app.get("/trips")
def get_trips():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trip_info")
    return cursor.fetchall()

@app.post("/add_trip")
def add_trip(trip: Trip):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trip_info (vehicle_number, fuel_consumption, trip_date,
            start_location, end_location, lat_start, lon_start, lat_end, lon_end, distance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trip.vehicle_number, trip.fuel_consumption, trip.trip_date,
          trip.start_location, trip.end_location, trip.lat_start,
          trip.lon_start, trip.lat_end, trip.lon_end, trip.distance))
    conn.commit()
    return {"message": "✅ Trip added successfully"}

@app.get("/analytics")
def get_analytics():
    cursor = conn.cursor()
    df = pd.read_sql_query("SELECT * FROM trip_info", conn)

    if df.empty:
        return {
            "Total Fuel": 0,
            "Total Distance": 0,
            "Average Mileage (km/l)": 0
        }

    total_fuel = df['fuel_consumption'].sum()
    total_distance = df['distance'].sum()
    avg_mileage = total_distance / total_fuel if total_fuel else 0

    return {
        "Total Fuel": round(total_fuel, 2),
        "Total Distance": round(total_distance, 2),
        "Average Mileage (km/l)": round(avg_mileage, 2)
    }
