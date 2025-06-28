import streamlit as st
from datetime import date
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# DB connection
conn = sqlite3.connect(r"C:\Users\MAYANK\Desktop\FleetStat\db\FleetStat.db", check_same_thread=False)
c = conn.cursor()

# Insert functions
def insert_vehicle(vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date):
    c.execute('''INSERT INTO vehicle_info (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date)
                 VALUES (?, ?, ?, ?, ?)''',
              (vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date))
    conn.commit()

def insert_trip(vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                lat_start, lon_start, lat_end, lon_end, distance):
    c.execute('''INSERT INTO trip_info (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
                 lat_start, lon_start, lat_end, lon_end, distance)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (vehicle_number, fuel_consumption, trip_date, start_location, end_location,
               lat_start, lon_start, lat_end, lon_end, distance))
    conn.commit()

# View functions
def view_vehicles():
    c.execute('SELECT * FROM vehicle_info')
    return c.fetchall()

def view_trips():
    c.execute('SELECT * FROM trip_info')
    return c.fetchall()

# Streamlit App
st.title("🚗 FleetStat - Track your Fleet")

menu = ["Add Vehicle", "Add Trip", "View Vehicles", "View Trips"]
choice = st.sidebar.selectbox("Select Action", menu)

# Add Vehicle UI
if choice == "Add Vehicle":
    st.subheader("Add Vehicle Info")
    vehicle_name = st.text_input("Vehicle Name")
    vehicle_number = st.text_input("Vehicle Number")
    owner_name = st.text_input("Owner Name")
    vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike", "Truck", "Bus"])
    registration_date = st.date_input("Registration Date", date.today())

    if st.button("Add Vehicle"):
        insert_vehicle(vehicle_name, vehicle_number, owner_name, vehicle_type, registration_date)
        st.success("✅ Vehicle added successfully")

# Add Trip UI
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
    distance = st.number_input("Distance (km)", min_value=0.0)

    if st.button("Add Trip"):
        insert_trip(vehicle_number, fuel, trip_date, start_location, end_location,
                    lat_start, lon_start, lat_end, lon_end, distance)
        st.success("✅ Trip added successfully")

# View Vehicles
elif choice == "View Vehicles":
    st.subheader("🚘 Vehicle List")

    # Load Data First
    query = """
        SELECT 
            v.vehicle_name,
            v.vehicle_number,
            v.owner_name,
            v.vehicle_type,
            v.registration_date,
            COUNT(t.trip_id) AS total_trips,
            COALESCE(SUM(t.distance), 0) AS total_distance_km
        FROM vehicle_info v
        LEFT JOIN trip_info t ON v.vehicle_number = t.vehicle_number
        GROUP BY v.vehicle_number
    """
    df = pd.read_sql_query(query, conn)

    # Rename Columns
    df.rename(columns={
        'vehicle_name': 'Vehicle Name',
        'vehicle_number': 'Vehicle Number',
        'owner_name': 'Owner Name',
        'vehicle_type': 'Vehicle Type',
        'registration_date': 'Registration Date',
        'total_trips': 'Total Trips',
        'total_distance_km': 'Total Distance (km)'
    }, inplace=True)

    # Search Filter
    search_term = st.text_input("🔍 Search by Vehicle Number").lower()
    if search_term:
        df = df[df["Vehicle Number"].str.lower().str.contains(search_term)]

    # Final Check
    if not df.empty:
        df.reset_index(drop=True, inplace=True)
        df.index = df.index + 1
        df.index.name = "S.No"

        # Download and Show Table
        st.download_button(
            label="📥 Download Vehicle Info as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='Vehicle_Info.csv',
            mime='text/csv'
        )
        st.dataframe(df)
    else:
        st.warning("No vehicles found matching the search term.")



# View Trips
elif choice == "View Trips":
    st.subheader("📋 Trip History")

    # Load trip data
    query = """
    SELECT 
        t.trip_id,
        t.vehicle_number,
        t.trip_date,
        t.start_location,
        t.end_location,
        t.distance,
        t.fuel_consumption,
        t.lat_start, t.lon_start, t.lat_end, t.lon_end
    FROM trip_info t
    ORDER BY t.trip_date DESC
    """
    df = pd.read_sql_query(query, conn)

    # Rename columns
    df.rename(columns={
        'trip_id': 'Trip ID',
        'vehicle_number': 'Vehicle Number',
        'trip_date': 'Trip Date',
        'start_location': 'Start Location',
        'end_location': 'End Location',
        'distance': 'Distance (km)',
        'fuel_consumption': 'Fuel Consumption (L)',
        'lat_start': 'Latitude Start',
        'lon_start': 'Longitude Start',
        'lat_end': 'Latitude End',
        'lon_end': 'Longitude End'
    }, inplace=True)

    # Apply date filters
    st.subheader("📅 Filter Trips by Date")
    if not df.empty:
        min_date = pd.to_datetime(df["Trip Date"]).min()
        max_date = pd.to_datetime(df["Trip Date"]).max()
        start_date = st.date_input("Start Date", value=min_date)
        end_date = st.date_input("End Date", value=max_date)
        df = df[(pd.to_datetime(df["Trip Date"]) >= pd.to_datetime(start_date)) &
                (pd.to_datetime(df["Trip Date"]) <= pd.to_datetime(end_date))]
    else:
        st.info("No trips available.")
        st.stop()

    # Search filter
    search_term = st.text_input("🔍 Search by Vehicle Number").lower()
    if search_term:
        df = df[df["Vehicle Number"].str.lower().str.contains(search_term)]

    # Final display table
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1
    df.index.name = "S.No"
    st.dataframe(df)

    # Show trip on map
    if not df.empty:
        trip_no = st.number_input("Enter Trip No. to View on Map", min_value=1, max_value=len(df), value=1)
        selected_trip = df.iloc[trip_no - 1]

        start_coords = (selected_trip['Latitude Start'], selected_trip['Longitude Start'])
        end_coords = (selected_trip['Latitude End'], selected_trip['Longitude End'])
        center_lat = (start_coords[0] + end_coords[0]) / 2
        center_lon = (start_coords[1] + end_coords[1]) / 2

        st.subheader(f"🗺️ Trip Map - Trip #{trip_no}")
        m = folium.Map(location=(center_lat, center_lon), zoom_start=10)
        folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color="red")).add_to(m)
        folium.PolyLine(locations=[start_coords, end_coords], color='blue').add_to(m)
        st_folium(m, width=700)

        # Trip fuel vs distance chart
        st.subheader("📊 Fuel vs Distance by Vehicle")
        chart_data = df.groupby("Vehicle Number")[["Distance (km)", "Fuel Consumption (L)"]].sum()
        st.bar_chart(chart_data)

        # Download
        st.download_button(
            label="📥 Download Trip Data as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='trip_data.csv',
            mime='text/csv'
        )
    else:
        st.warning("No trips match the selected filters.")


# Add Google Maps API to track location
#
# Show fuel cost estimates
#
# Predict next fuel refill using average data
#
# Create a dashboard for each vehicle
#
# Allow user to upload CSV trips