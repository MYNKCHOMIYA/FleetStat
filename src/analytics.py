import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../db/FleetStat.db")

def get_trip_analytics():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trip_info", conn)
    conn.close()

    result = {}

    if df.empty:
        return result

    total_distance = df["distance"].sum()
    total_fuel = df["fuel_consumption"].sum()
    avg_mileage = round(total_distance / total_fuel, 2) if total_fuel > 0 else 0

    result["Total Distance"] = round(total_distance, 2)
    result["Total Fuel"] = round(total_fuel, 2)
    result["Average Mileage (km/l)"] = avg_mileage

    # Per-trip stats
    for trip_id in df["trip_id"].unique():
        trip_df = df[df["trip_id"] == trip_id]
        d = trip_df["distance"].sum()
        f = trip_df["fuel_consumption"].sum()
        m = round(d / f, 2) if f > 0 else 0

        result[f"Total Distance of {trip_id} trip"] = round(d, 2)
        result[f"Total Fuel used in {trip_id} trip"] = round(f, 2)
        result[f"Average Mileage in {trip_id} trip (km/l)"] = m

    return result
