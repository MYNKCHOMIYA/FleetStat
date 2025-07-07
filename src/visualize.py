import folium
from folium.plugins import HeatMap, MarkerCluster
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# ========== 1️⃣ FOLIUM MAPPING FUNCTIONS ==========

def generate_route_map(lat_start, lon_start, lat_end, lon_end):
    center = [(lat_start + lat_end) / 2, (lon_start + lon_end) / 2]
    m = folium.Map(location=center, zoom_start=10)

    folium.Marker([lat_start, lon_start], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([lat_end, lon_end], tooltip="End", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine([[lat_start, lon_start], [lat_end, lon_end]], color="blue").add_to(m)

    return m

def generate_trip_heatmap(df):
    heat_data = df[['lat_start', 'lon_start']].dropna().values.tolist()
    heat_data += df[['lat_end', 'lon_end']].dropna().values.tolist()

    m = folium.Map(location=[26.9, 75.8], zoom_start=6)
    HeatMap(heat_data).add_to(m)
    return m

def generate_cluster_map(df):
    m = folium.Map(location=[26.9, 75.8], zoom_start=6)
    cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        folium.Marker(
            [row['lat_start'], row['lon_start']],
            popup=f"Trip {row['trip_number']} | {row['vehicle_number']} - Start"
        ).add_to(cluster)

        folium.Marker(
            [row['lat_end'], row['lon_end']],
            popup=f"Trip {row['trip_number']} | {row['vehicle_number']} - End"
        ).add_to(cluster)

    return m

# ========== 2️⃣ SIMULATED DATA ==========

data = {
    'trip_number': np.arange(1, 21),
    'vehicle_number': [f"RJ14XX{str(i).zfill(4)}" for i in range(1, 21)],
    'lat_start': np.random.uniform(26.5, 27.5, 20),
    'lon_start': np.random.uniform(75.5, 76.5, 20),
    'lat_end': np.random.uniform(26.5, 27.5, 20),
    'lon_end': np.random.uniform(75.5, 76.5, 20),
    'fuel_consumption': np.random.uniform(5, 15, 20)
}
df = pd.DataFrame(data)

# ========== 3️⃣ DISPLAY MAPS IN STREAMLIT ==========

st.set_page_config(layout="wide")
st.title("🗺 FleetStat Maps Preview (Testing Mode)")

tab1, tab2, tab3, tab4 = st.tabs(["Route Map", "Heatmap", "Cluster Map", "Fuel Chart"])

with tab1:
    st.subheader("📍 Route Map for Trip 1")
    route_map = generate_route_map(
        df.loc[0, 'lat_start'],
        df.loc[0, 'lon_start'],
        df.loc[0, 'lat_end'],
        df.loc[0, 'lon_end']
    )
    st_folium(route_map, width=700, height=500)

with tab2:
    st.subheader("🔥 Heatmap of All Trips")
    heatmap = generate_trip_heatmap(df)
    st_folium(heatmap, width=700, height=500)

with tab3:
    st.subheader("📌 Cluster Map of All Trips")
    cluster_map = generate_cluster_map(df)
    st_folium(cluster_map, width=700, height=500)

with tab4:
    st.subheader("⛽ Fuel Consumption Per Trip")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['trip_number'], df['fuel_consumption'], label='Fuel Consumption', color='green', linestyle='-', marker='o')
    ax.set_title('Fuel Consumption per Trip')
    ax.set_xlabel('Trip Number')
    ax.set_ylabel('Fuel (liters)')
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
