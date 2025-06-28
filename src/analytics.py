# analytics.py
import pandas as pd
from db_handler import conn  # ✅ Reuse existing DB connection

def get_trip_analytics():
    try:
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

    except Exception as e:
        return {"error": str(e)}
