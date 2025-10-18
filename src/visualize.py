import folium
from folium.plugins import HeatMap
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# ========== FOLIUM HEATMAP FUNCTION ==========

def generate_trip_heatmap(df):
    heat_data = df[['lat_start', 'lon_start']].dropna().values.tolist()
    heat_data += df[['lat_end', 'lon_end']].dropna().values.tolist()

    m = folium.Map(location=[26.9, 75.8], zoom_start=6)
    HeatMap(heat_data).add_to(m)
    return m


