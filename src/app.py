import streamlit as st
from datetime import date
import sqlite3
import requests
import pandas as pd
from streamlit_folium import st_folium
from geopy.distance import geodesic
import folium
import os
import polyline

# ---------------- API Key ----------------
API_KEY = "x"

# ---------------- Google Directions Function ----------------
def get_route_polyline(start_loc, end_loc, api_key):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": start_loc,
        "destination": end_loc,
        "key": api_key,
        "mode": "driving"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        overview_polyline = data["routes"][0]["overview_polyline"]["points"]
        points = polyline.decode(overview_polyline)
        return points
    else:
        st.warning(f"Google Directions API error: {data.get('status')}")
        if "error_message" in data:
            st.error(data["error_message"])
    return []

# ---------------- Google Distance Function ----------------
def get_road_distance_google(start_loc, end_loc, api_key):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": start_loc,
        "destinations": end_loc,
        "key": api_key,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        element = data["rows"][0]["elements"][0]
        if element["status"] == "OK":
            distance_text = element["distance"]["text"]
            distance_value = element["distance"]["value"] / 1000
            return distance_text, distance_value
    return None, 0.0

# ---------------- Imports for Custom Modules ----------------
from db_handler import insert_vehicle, insert_trip, view_vehicles, view_trips
from analytics import get_trip_analytics
from visualize import generate_route_map, generate_trip_heatmap, generate_cluster_map

# ---------------- Streamlit Config ----------------
st.set_page_config(layout="wide")
st.title("🚗 FleetStat - Track Your Fleet")

# Sidebar menu
menu = ["Dashboard", "Add Vehicle", "Add Trip", "View Vehicles", "View Trips", "Heatmap", "Per-Trip Analytics"]
choice = st.sidebar.selectbox("Select Option", menu)

# SQLite connection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../db/FleetStat.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# ---------------- Dashboard ----------------
if choice == "Dashboard":
    st.subheader("📈 Fleet Overview Dashboard")
    analytics = get_trip_analytics()

    col1, col2, col3 = st.columns(3)
    col1.metric("🚣 Total Distance", f"{analytics.get('Total Distance', '0')} km")
    col2.metric("⛽ Total Fuel Used", f"{analytics.get('Total Fuel', '0')} L")
    col3.metric("⚡ Avg Mileage", f"{analytics.get('Average Mileage (km/l)', '0')} km/L")

    st.markdown("---")
    st.subheader("🔍 Trip Specific Stats & Route")

    st.subheader("🌍 Trip Heatmap")
    df = pd.read_sql_query("SELECT * FROM trip_info", conn)

    if not df.empty:
        heatmap = generate_trip_heatmap(df)
        st_folium(heatmap, width=700)
    else:
        st.warning("No trip data available.")

# ---------------- Add Vehicle ----------------
elif choice == "Add Vehicle":
    st.subheader("Add Vehicle Info")
    vehicle_name = st.text_input("Vehicle Name")
    vehicle_number = st.text_input("Vehicle Number")
    owner_name = st.text_input("Owner Name")
    vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike", "Truck", "Bus"])
    registration_date = st.date_input("Registration Date", date.today())

    if st.button("Add Vehicle"):
        insert_vehicle(vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date)
        st.success("✅ Vehicle added successfully.")

# ---------------- Add Trip ----------------
elif choice == "Add Trip":
    st.subheader("Add Trip Info")
    vehicle_number = st.text_input("Vehicle Number")
    fuel = st.number_input("Fuel Used (L)", min_value=0.0)
    trip_date = st.date_input("Trip Date", date.today())
    start_location = st.text_input("Start Location")
    end_location = st.text_input("End Location")
    lat_start = st.number_input("Latitude Start")
    lon_start = st.number_input("Longitude Start")
    lat_end = st.number_input("Latitude End")
    lon_end = st.number_input("Longitude End")

    if st.button("Add Trip"):
        if start_location and end_location:
            distance_text, distance = get_road_distance_google(start_location, end_location, API_KEY)
            if distance == 0.0:
                st.error("⚠️ Could not fetch distance. Trip not saved.")
            else:
                insert_trip(
                    vehicle_number,
                    fuel,
                    trip_date,
                    start_location,
                    end_location,
                    lat_start,
                    lon_start,
                    lat_end,
                    lon_end,
                    distance
                )
                st.success(f"✅ Trip added successfully. Distance: {distance_text}")

                m = folium.Map(location=[(lat_start + lat_end) / 2, (lon_start + lon_end) / 2], zoom_start=7)
                folium.Marker([lat_start, lon_start], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
                folium.Marker([lat_end, lon_end], tooltip="End", icon=folium.Icon(color="red")).add_to(m)

                route_points = get_route_polyline(start_location, end_location, API_KEY)
                if route_points:
                    folium.PolyLine(route_points, color="blue", weight=4).add_to(m)

                st.subheader("🗺 Trip Route")
                st_folium(m, width=700, height=500)
        else:
            st.error("❗ Please enter both start and end locations.")

# ---------------- View Vehicles ----------------
elif choice == "View Vehicles":
    st.subheader("🚘 Vehicle List")
    df = pd.read_sql_query('''
        SELECT 
            v.vehicle_name AS "Vehicle Name",
            v.vehicle_number AS "Vehicle Number",
            v.owner_name AS "Owner Name",
            v.vehicle_type AS "Vehicle Type",
            v.registration_date AS "Registration Date",
            COUNT(t.trip_id) AS "Total Trips",
            COALESCE(SUM(t.distance), 0) AS "Total Distance (km)"
        FROM vehicle_info v
        LEFT JOIN trip_info t ON v.vehicle_number = t.vehicle_number
        GROUP BY v.vehicle_number
    ''', conn)

    search_term = st.text_input("🔍 Search by Vehicle Number").lower()
    if search_term:
        df = df[df["Vehicle Number"].str.lower().str.contains(search_term)]

    if not df.empty:
        st.download_button("Download CSV", df.to_csv(index=False).encode(), "vehicles.csv")
        st.dataframe(df)
    else:
        st.warning("No vehicles found.")

# ---------------- View Trips ----------------
elif choice == "View Trips":
    st.subheader("📋 Trip History")
    df = pd.read_sql_query("SELECT * FROM trip_info ORDER BY trip_date DESC", conn)

    if not df.empty:
        min_date = pd.to_datetime(df["trip_date"]).min().date()
        max_date = pd.to_datetime(df["trip_date"]).max().date()
        start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

        df = df[
            (pd.to_datetime(df["trip_date"]).dt.date >= start_date) &
            (pd.to_datetime(df["trip_date"]).dt.date <= end_date)
        ]

        search_term = st.text_input("Search by Vehicle Number").lower()
        if search_term:
            df = df[df["vehicle_number"].str.lower().str.contains(search_term)]

        st.dataframe(df)
        analytics = get_trip_analytics()
        df_trips = view_trips()
    if not df_trips.empty:
        trip_ids = df_trips["trip_id"].tolist()
        selected_trip_id = st.selectbox("Select Trip ID", trip_ids)

        distance_key = f"Total Distance of {selected_trip_id} trip"
        fuel_key = f"Total Fuel used in {selected_trip_id} trip"
        mileage_key = f"Average Mileage in {selected_trip_id} trip (km/l)"

        col4, col5, col6 = st.columns(3)
        col4.metric("🚗 Trip Distance", f"{analytics.get(distance_key, 'N/A')} km")
        col5.metric("⛽ Fuel Used", f"{analytics.get(fuel_key, 'N/A')} L")
        col6.metric("⚡ Avg Mileage", f"{analytics.get(mileage_key, 'N/A')} km/L")

        trip = df_trips[df_trips["trip_id"] == selected_trip_id].iloc[0]
        start_loc = trip["start_location"]
        end_loc = trip["end_location"]
        lat_start = trip["lat_start"]
        lon_start = trip["lon_start"]
        lat_end = trip["lat_end"]
        lon_end = trip["lon_end"]

        m = folium.Map(location=[(lat_start + lat_end) / 2, (lon_start + lon_end) / 2], zoom_start=7)

        folium.Marker([lat_start, lon_start], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker([lat_end, lon_end], tooltip="End", icon=folium.Icon(color="red")).add_to(m)

        route_points = get_route_polyline(start_loc, end_loc, API_KEY)
        if route_points:
            folium.PolyLine(route_points, color="blue", weight=4).add_to(m)
        else:
            st.warning("⚠️ Road route could not be fetched.")

        st.subheader("🗺 Road Route on Map")
        st_folium(m, width=700, height=500)
    else:
        st.warning("No trip data available.")

# ---------------- Heatmap ----------------
elif choice == "Heatmap":
    st.subheader("🌍 Trip Heatmap")
    df = pd.read_sql_query("SELECT * FROM trip_info", conn)

    if not df.empty:
        heatmap = generate_trip_heatmap(df)
        st_folium(heatmap, width=700)
    else:
        st.warning("No data to display heatmaps.")

# ---------------- Per-Trip Analytics ----------------
elif choice == "Per-Trip Analytics":
    st.subheader("📊 Per-Trip Fuel Consumption Analysis")

    df = pd.read_sql_query("SELECT trip_id, trip_date, vehicle_number, fuel_consumption FROM trip_info ORDER BY trip_date ASC", conn)

    if not df.empty:
        df["trip_date"] = pd.to_datetime(df["trip_date"]).dt.strftime("%Y-%m-%d")
        st.dataframe(df)

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(
            df["trip_id"],
            df["fuel_consumption"],
            marker=".",
            color="black",
            linestyle="-"
        )
        ax.set_title("Fuel Consumption per Trip")
        ax.set_xlabel("Trip ID")
        ax.set_ylabel("Fuel Consumption (liters)")
        ax.grid(True)

        st.pyplot(fig)

    else:
        st.warning("No trip data available to plot.")
