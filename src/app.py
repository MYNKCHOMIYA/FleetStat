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
API_KEY = "enter api key here" # Replace with your actual Google API key

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

    print("🔍 Google Directions API Response:", data)

    if data.get("status") == "OK":
        overview_polyline = data["routes"][0]["overview_polyline"]["points"]
        # Decode the polyline into lat/lon pairs
        points = polyline.decode(overview_polyline)
        return points
    else:
        print("⚠️ Directions API error:", data.get("status"))
        if "error_message" in data:
            print("❌ Error Message:", data["error_message"])
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

    # Debug logging
    print("🔍 Google API Response:", data)

    if data.get("status") == "OK":
        element = data["rows"][0]["elements"][0]
        if element["status"] == "OK":
            distance_text = element["distance"]["text"]
            distance_value = element["distance"]["value"] / 1000
            print(f"✅ Returning distance: {distance_text}, {distance_value} km")
            return distance_text, distance_value
        else:
            print("⚠️ Element status error:", element["status"])
    else:
        print("⚠️ API status error:", data.get("status"))
        if "error_message" in data:
            print("❌ Error Message:", data["error_message"])

    return None, 0.0

# ---------------- Imports for Custom Modules ----------------
from db_handler import insert_vehicle, insert_trip, view_vehicles, view_trips
from analytics import get_trip_analytics
from visualize import generate_route_map, generate_trip_heatmap, generate_cluster_map

# ---------------- Streamlit Config ----------------
st.set_page_config(layout="wide")
st.title("🚗 FleetStat - Track Your Fleet")

# Sidebar menu
menu = ["Dashboard", "Add Vehicle", "Add Trip", "View Vehicles", "View Trips", "Heatmap"]
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
    col1.metric("🚣 Total Distance", f"{analytics['Total Distance']} km")
    col2.metric("⛽ Total Fuel Used", f"{analytics['Total Fuel']} L")
    col3.metric("⚡ Avg Mileage", f"{analytics['Average Mileage (km/l)']} km/L")

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
        st.success("✅ Vehicle added successfully")

# ---------------- Add Trip ----------------
elif choice == "Add Trip":
    st.subheader("Add Trip Info")

    vehicle_number = st.text_input("Vehicle Number")
    fuel = st.number_input("Fuel Used (L)", min_value=0.0)
    trip_date = st.date_input("Trip Date", date.today())
    start_location = st.text_input("Start Location (City name or full address)")
    end_location = st.text_input("End Location (City name or full address)")
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

                # Show route map
                m = generate_route_map(lat_start, lon_start, lat_end, lon_end)
                st.subheader("🗺 Trip Route")
                st_folium(m, width=700, height=500)
        else:
            st.error("❗ Please enter both start and end locations before adding the trip.")

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

        if not df.empty:
            # Let user pick which trip to view
            trip_ids = df["trip_id"].tolist()
            selected_trip_id = st.selectbox("Select Trip ID to view route", trip_ids)

            # Get the selected trip row
            trip = df[df["trip_id"] == selected_trip_id].iloc[0]

            # Safely handle possible column names
            start_loc = trip.get("start_location") or trip.get("Start Location")
            end_loc = trip.get("end_location") or trip.get("End Location")

            # Create the map
            m = folium.Map(
                location=[(trip["lat_start"] + trip["lat_end"]) / 2,
                          (trip["lon_start"] + trip["lon_end"]) / 2],
                zoom_start=7
            )

            # Add start/end markers
            folium.Marker(
                [trip["lat_start"], trip["lon_start"]],
                tooltip="Start",
                icon=folium.Icon(color="green")
            ).add_to(m)
            folium.Marker(
                [trip["lat_end"], trip["lon_end"]],
                tooltip="End",
                icon=folium.Icon(color="red")
            ).add_to(m)

            # Fetch and draw the real driving route
            route_points = get_route_polyline(start_loc, end_loc, API_KEY)
            if route_points:
                folium.PolyLine(route_points, color="blue", weight=4).add_to(m)
            else:
                folium.PolyLine(
                    [[trip["lat_start"], trip["lon_start"]],
                     [trip["lat_end"], trip["lon_end"]]],
                    color="gray",
                    dash_array="5,5"
                ).add_to(m)

            st.subheader("🗺 Trip Route")
            st_folium(m, width=700)

            # Bar chart
            chart_data = df.groupby("vehicle_number")[["distance", "fuel_consumption"]].sum()
            st.subheader("📊 Fuel vs Distance")
            st.bar_chart(chart_data)
    else:
        st.warning("No trip data available.")

# ---------------- Heatmap ----------------
elif choice == "Heatmap":
    st.subheader("🌍 Trip Heatmap")
    df = pd.read_sql_query("SELECT * FROM trip_info", conn)

    if not df.empty:
        heatmap = generate_trip_heatmap(df)
        st_folium(heatmap, width=700)

        st.subheader("🗺 Cluster Map")
        cluster_map = generate_cluster_map(df)
        st_folium(cluster_map, width=700)
    else:
        st.warning("No data to display heatmaps.")
