import folium
from folium.plugins import HeatMap, MarkerCluster
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
# Simulate trip data (for testing)
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

# ========== 3️⃣ GENERATE MAPS ==========

# Route map for trip 1
route_map = generate_route_map(
    df.loc[0, 'lat_start'],
    df.loc[0, 'lon_start'],
    df.loc[0, 'lat_end'],
    df.loc[0, 'lon_end']
)
route_map.save("route_map.html")

# Heatmap of all trips
heatmap = generate_trip_heatmap(df)
heatmap.save("heatmap.html")

# Cluster map of all trips
cluster_map = generate_cluster_map(df)
cluster_map.save("cluster_map.html")

# ========== 4️⃣ MATPLOTLIB PER-TRIP FUEL CONSUMPTION PLOT ==========
plt.figure(figsize=(10, 5))
plt.plot(
    df['trip_number'],
    df['fuel_consumption'],
    label='Fuel Consumption per Trip',
    color='green',
    linestyle='-',
    marker='o'
)

plt.title('Fuel Consumption per Trip - FleetStat')
plt.xlabel('Trip Number')
plt.ylabel('Fuel Consumption (liters)')
plt.xticks(df['trip_number'])
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save plot to a file
plt.savefig("fuel_consumption_per_trip.png")

# Display in Python (or comment out if running headless)
plt.show()

print("✅ All visualizations generated successfully.")
