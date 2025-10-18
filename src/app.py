import streamlit as st
import pandas as pd
import sqlite3
import requests
import joblib
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
from geopy.distance import geodesic
from datetime import datetime, date
import os
import polyline
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# ================== ENV SETUP =====================
load_dotenv()   
API_KEY = os.getenv("GOOGLE_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER") 
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ============== DATABASE CONNECTION ==============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../db/FleetStat.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# ============== DARK MODE CONFIG ==============
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if st.session_state.dark_mode:
    st.markdown("""
        <style>
        body {
            background-color: #000;
            color: #eee;
        }
        .stApp {
            background-color: #000;
        }
        </style>
    """, unsafe_allow_html=True)


# ============== LOGIN ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login"):
        st.title("🔒 FleetStat Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")
        if login:
            if user == "admin" and pwd == "admin":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid Credentials")
    st.stop()

# ============== UI SETUP ===================
st.set_page_config(layout="wide", page_title="FleetStat Dashboard", page_icon="🚗")
st.title("🚗 FleetStat - Smarter Fleet Tracking")

with st.sidebar:
    st.image("logo.png", width=200)
    st.header("📋 Navigation")
    menu = ["Dashboard", "Add Vehicle", "Add Trip", "View Vehicles", "View Trips", "Per-Trip Analytics"]
    choice = st.selectbox("Select Option", menu)
    st.markdown("---")
    st.info("Tip: Use filters to refine your data view.")
    dark_toggle = st.toggle("🌗 Dark Mode", value=st.session_state.dark_mode)
    if dark_toggle != st.session_state.dark_mode:
     st.session_state.dark_mode = dark_toggle
     st.rerun()



# ---------------- Google Directions Function ----------------
def get_route_polyline(start_loc, end_loc,API_KEY):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": start_loc,
        "destination": end_loc,
        "key": API_KEY,
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
def get_road_distance_google(start_loc, end_loc, API_KEY):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": start_loc,
        "destinations": end_loc,
        "key": API_KEY,
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
from visualize import generate_trip_heatmap

# SQLite connection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../db/FleetStat.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# ---------------- Dashboard ----------------
if choice == "Dashboard":
    st.subheader("📈 Fleet Overview Dashboard")
    analytics = get_trip_analytics()

    col1, col2, col3 = st.columns(3)
    col1.metric("🚗 Total Distance", f"{analytics.get('Total Distance', '0')} km")
    col2.metric("⛽ Total Fuel Used", f"{analytics.get('Total Fuel', '0')} L")
    col3.metric("⚡ Avg Mileage", f"{analytics.get('Average Mileage (km/l)', '0')} km/L")

    st.markdown("---")
    st.subheader("🌍 Trip Heatmap")
    df = pd.read_sql_query("SELECT * FROM trip_info", conn)

    if not df.empty:
        heatmap = generate_trip_heatmap(df)
        st_folium(heatmap, width=700)
    else:
        st.warning("No trip data available.")

# ---------------- Add Vehicle ----------------
elif choice == "Add Vehicle":
    st.subheader("🚘 Add or Update Vehicle")

    df_vehicles = pd.read_sql_query("SELECT * FROM vehicle_info", conn)
    vehicle_numbers = df_vehicles["vehicle_number"].tolist()

    selected_vehicle = st.selectbox("Select Vehicle to Update or Leave Blank to Add New", [""] + vehicle_numbers)
    existing = df_vehicles[df_vehicles["vehicle_number"] == selected_vehicle].iloc[0] if selected_vehicle else None

    with st.form("vehicle_form"):
        vehicle_name = st.text_input("Vehicle Name", existing["vehicle_name"] if existing is not None else "")
        vehicle_number = st.text_input("Vehicle Number", selected_vehicle if selected_vehicle else "")
        owner_name = st.text_input("Owner Name", existing["owner_name"] if existing is not None else "")
        vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike", "Truck", "Bus"],
                                    index=["Car", "Bike", "Truck", "Bus"].index(existing["vehicle_type"]) if existing is not None else 0)
        registration_date = st.date_input("Registration Date", pd.to_datetime(existing["registration_date"]).date() if existing is not None else date.today())

        if st.form_submit_button("Save Vehicle Info"):
            if selected_vehicle:
                conn.execute("""
                    UPDATE vehicle_info SET
                        vehicle_name=?, owner_name=?, vehicle_type=?, registration_date=?
                    WHERE vehicle_number=?
                """, (vehicle_name, owner_name, vehicle_type, registration_date, vehicle_number))
                conn.commit()
                st.success("✅ Vehicle updated successfully.")
            else:
                insert_vehicle(vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date)
                st.success("✅ New vehicle added successfully.")
# ---------------- Add Trip ----------------
elif choice == "Add Trip":
    st.subheader("🛣️ Add or Update Trip")

    df_trips = pd.read_sql_query("SELECT * FROM trip_info ORDER BY trip_date DESC", conn)
    trip_ids = df_trips["trip_id"].tolist()
    selected_trip = st.selectbox("Select Trip ID to Update or Leave Blank to Add New", [""] + trip_ids)
    existing = df_trips[df_trips["trip_id"] == selected_trip].iloc[0] if selected_trip else None

    with st.form("trip_form"):
        vehicle_number = st.text_input("Vehicle Number", existing["vehicle_number"] if existing is not None else "")
        fuel = st.number_input("Fuel Used (L)", min_value=0.0, value=existing["fuel_consumption"] if existing is not None else 0.0)
        trip_date = st.date_input("Trip Date", pd.to_datetime(existing["trip_date"]).date() if existing is not None else date.today())
        start_location = st.text_input("Start Location", existing["start_location"] if existing is not None else "")
        end_location = st.text_input("End Location", existing["end_location"] if existing is not None else "")
        lat_start = st.number_input("Latitude Start", value=existing["lat_start"] if existing is not None else 0.0)
        lon_start = st.number_input("Longitude Start", value=existing["lon_start"] if existing is not None else 0.0)
        lat_end = st.number_input("Latitude End", value=existing["lat_end"] if existing is not None else 0.0)
        lon_end = st.number_input("Longitude End", value=existing["lon_end"] if existing is not None else 0.0)

        if st.form_submit_button("Save Trip Info"):
            distance_text, distance = get_road_distance_google(start_location, end_location, API_KEY)
            if distance == 0.0:
                st.error("⚠️ Could not fetch distance. Trip not saved.")
            else:
                if selected_trip:
                    conn.execute("""
                        UPDATE trip_info SET
                            vehicle_number=?, fuel_consumption=?, trip_date=?,
                            start_location=?, end_location=?,
                            lat_start=?, lon_start=?, lat_end=?, lon_end=?, distance=?
                        WHERE trip_id=?
                    """, (vehicle_number, fuel, trip_date, start_location, end_location,
                          lat_start, lon_start, lat_end, lon_end, distance, selected_trip))
                    conn.commit()
                    st.success("✅ Trip updated successfully!")
                else:
                    insert_trip(vehicle_number, fuel, trip_date, start_location, end_location,
                                lat_start, lon_start, lat_end, lon_end, distance)
                    st.success(f"✅ Trip added successfully. Distance: {distance_text}")

                m = folium.Map(location=[(lat_start + lat_end) / 2, (lon_start + lon_end) / 2], zoom_start=7)
                folium.Marker([lat_start, lon_start], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
                folium.Marker([lat_end, lon_end], tooltip="End", icon=folium.Icon(color="red")).add_to(m)
                route_points = get_route_polyline(f"{lat_start},{lon_start}", f"{lat_end},{lon_end}", API_KEY)
                if route_points:
                    folium.PolyLine(route_points, color="blue", weight=4).add_to(m)
                st.subheader("🗺 Trip Route")
                st_folium(m, width=700, height=500)


# ---------------- View Vehicles ----------------
elif choice == "View Vehicles":
    st.subheader("🚙 Vehicle Overview")
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

        df = df[(pd.to_datetime(df["trip_date"]).dt.date >= start_date) & (pd.to_datetime(df["trip_date"]).dt.date <= end_date)]

        search_term = st.text_input("Search by Vehicle Number").lower()
        if search_term:
            df = df[df["vehicle_number"].str.lower().str.contains(search_term)]

        st.dataframe(df)
        analytics = get_trip_analytics()
        df_trips = view_trips()
        if not df_trips.empty:
            trip_ids = df_trips["trip_id"].tolist()
            selected_trip_id = st.selectbox("Select Trip ID", trip_ids)

            trip = df_trips[df_trips["trip_id"] == selected_trip_id].iloc[0]
            start_loc = trip["start_location"]
            end_loc = trip["end_location"]
            lat_start = trip["lat_start"]
            lon_start = trip["lon_start"]
            lat_end = trip["lat_end"]
            lon_end = trip["lon_end"]

            distance_key = f"Total Distance of {selected_trip_id} trip"
            fuel_key = f"Total Fuel used in {selected_trip_id} trip"
            mileage_key = f"Average Mileage in {selected_trip_id} trip (km/l)"

            col4, col5, col6 = st.columns(3)
            col4.metric("🚗 Trip Distance", f"{analytics.get(distance_key, 'N/A')} km")
            col5.metric("⛽ Fuel Used", f"{analytics.get(fuel_key, 'N/A')} L")
            col6.metric("⚡ Avg Mileage", f"{analytics.get(mileage_key, 'N/A')} km/L")

            m = folium.Map(location=[(lat_start + lat_end) / 2, (lon_start + lon_end) / 2], zoom_start=7)
            folium.Marker([lat_start, lon_start], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
            folium.Marker([lat_end, lon_end], tooltip="End", icon=folium.Icon(color="red")).add_to(m)
            origin = f"{lat_start},{lon_start}"
            destination = f"{lat_end},{lon_end}"
            route_points = get_route_polyline(origin, destination, API_KEY)
            if route_points:
                folium.PolyLine(route_points, color="blue", weight=4).add_to(m)
            else:
                st.warning("⚠️ Could not fetch driving route. Showing only markers.")

            st.subheader("🗺 Trip-Specific Route Map")
            st_folium(m, width=700, height=500)
        else:
            st.warning("No trip data available.")

# ---------------- Per-Trip Analytics ----------------

elif choice == "Per-Trip Analytics":
    st.subheader("📊 Per-Trip Fuel Consumption Analysis")
    st.markdown("### Analyze how much fuel is consumed per trip across your fleet.")

    df = pd.read_sql_query(
        "SELECT trip_id, trip_date, vehicle_number, fuel_consumption FROM trip_info ORDER BY trip_date ASC",
        conn
    )

    if not df.empty:
        df["trip_date"] = pd.to_datetime(df["trip_date"])
        
        # Optional filters
        with st.expander("🔍 Filter trips"):
            col1, col2 = st.columns(2)
            with col1:
                selected_vehicle = st.selectbox("Select Vehicle", options=["All"] + sorted(df["vehicle_number"].unique().tolist()))
            with col2:
                date_range = st.date_input("Select Date Range", value=[df["trip_date"].min(), df["trip_date"].max()])

        # Apply filters
        if selected_vehicle != "All":
            df = df[df["vehicle_number"] == selected_vehicle]
        df = df[(df["trip_date"] >= pd.to_datetime(date_range[0])) & (df["trip_date"] <= pd.to_datetime(date_range[1]))]

        if not df.empty:
            # Animated and interactive chart
            import plotly.express as px
            fig = px.line(
                df,
                x="trip_date",
                y="fuel_consumption",
                color="vehicle_number",
                markers=True,
                title="🚚 Fuel Consumption Over Time",
                labels={"trip_date": "Trip Date", "fuel_consumption": "Fuel (liters)", "vehicle_number": "Vehicle"},
                template="plotly_white",
            )
            fig.update_traces(line=dict(width=2), marker=dict(size=8))
            fig.update_layout(hovermode="x unified", transition_duration=500)

            st.plotly_chart(fig, use_container_width=True)

            # Stats summary
            st.markdown("### 📌 Trip Summary Stats")
            col1, col2, col3 = st.columns(3)
            col1.metric("🔻 Min Fuel Used", f"{df['fuel_consumption'].min():.2f} L")
            col2.metric("🔺 Max Fuel Used", f"{df['fuel_consumption'].max():.2f} L")
            col3.metric("📉 Avg Fuel Used", f"{df['fuel_consumption'].mean():.2f} L")

            st.dataframe(df.sort_values("trip_date"), use_container_width=True)
        else:
            st.warning("No trip data found for selected filters.")
    else:
        st.warning("No trip data available to display.")









