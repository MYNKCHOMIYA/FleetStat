import folium
from folium.plugins import HeatMap, MarkerCluster

# Map with start & end route line
def generate_route_map(lat_start, lon_start, lat_end, lon_end):
    center = [(lat_start + lat_end) / 2, (lon_start + lon_end) / 2]
    m = folium.Map(location=center, zoom_start=10)

    folium.Marker([lat_start, lon_start], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([lat_end, lon_end], tooltip="End", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine([[lat_start, lon_start], [lat_end, lon_end]], color="blue").add_to(m)

    return m

# Heatmap of all trip start/end coordinates
def generate_trip_heatmap(df):
    heat_data = df[['lat_start', 'lon_start']].dropna().values.tolist()
    heat_data += df[['lat_end', 'lon_end']].dropna().values.tolist()

    m = folium.Map(location=[26.9, 75.8], zoom_start=6)
    HeatMap(heat_data).add_to(m)
    return m

# Marker cluster map
def generate_cluster_map(df):
    m = folium.Map(location=[26.9, 75.8], zoom_start=6)
    cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        folium.Marker(
            [row['lat_start'], row['lon_start']],
            popup=f"{row['vehicle_number']} - Start"
        ).add_to(cluster)
        folium.Marker(
            [row['lat_end'], row['lon_end']],
            popup=f"{row['vehicle_number']} - End"
        ).add_to(cluster)

    return m
