import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import plotly.express as px

# App Config
st.set_page_config(
    page_title="AI Environmental Impact Tracker",
    page_icon="🌍",
    layout="wide"
)

# Title
st.title("🌍 AI-Powered Environmental Impact Tracker")

# Sidebar - User Inputs
with st.sidebar:
    st.header("Your Carbon Profile")
    
    # Transport
    transport_mode = st.selectbox(
        "Primary Transport Mode",
        ["Car", "Bus", "Train", "Bicycle", "Walking"]
    )
    distance = st.slider("Daily Distance (km)", 0, 100, 10)
    
    # Energy
    energy = st.number_input("Monthly Energy Usage (kWh)", min_value=0, value=300)
    
    # Location
    location = st.text_input("Your City", "London")
    
    # Advanced
    with st.expander("Advanced Settings"):
        diet = st.selectbox(
            "Diet Type",
            ["Omnivore", "Vegetarian", "Vegan"],
            index=0
        )

# Calculate Carbon Footprint (Mock AI)
def calculate_footprint(transport, dist, energy_use, diet_type):
    # Simple calculation (replace with your AI model)
    transport_factors = {"Car": 0.3, "Bus": 0.1, "Train": 0.05, "Bicycle": 0.01, "Walking": 0}
    diet_factors = {"Omnivore": 2.5, "Vegetarian": 1.5, "Vegan": 1.0}
    
    transport_co2 = dist * 365 * transport_factors[transport]
    energy_co2 = energy_use * 0.5  # kg per kWh
    diet_co2 = diet_factors[diet_type] * 365
    
    return transport_co2 + energy_co2 + diet_co2

# Get Coordinates for Map
def get_coordinates(city):
    geolocator = Nominatim(user_agent="env_app")
    location = geolocator.geocode(city)
    if location:
        return [location.latitude, location.longitude]
    return [51.5074, -0.1278]  # Default to London

# Calculations
total_co2 = calculate_footprint(transport_mode, distance, energy, diet)
co2_breakdown = {
    "Transport": distance * 365 * {"Car": 0.3, "Bus": 0.1, "Train": 0.05, "Bicycle": 0.01, "Walking": 0}[transport_mode],
    "Energy": energy * 0.5,
    "Diet": {"Omnivore": 2.5, "Vegetarian": 1.5, "Vegan": 1.0}[diet] * 365
}

# Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.metric("Annual CO₂ Footprint", f"{total_co2:,.0f} kg")
    
    # Recommendations
    if total_co2 > 10000:
        st.error("🚨 High Impact Area - Consider reducing car and meat consumption")
    elif total_co2 > 5000:
        st.warning("⚠️ Moderate Impact - Try using public transport more often")
    else:
        st.success("✅ Sustainable Lifestyle!")

with col2:
    # Impact Breakdown Chart
    df = pd.DataFrame({
        "Category": list(co2_breakdown.keys()),
        "CO2 (kg)": list(co2_breakdown.values())
    })
    fig = px.pie(df, values="CO2 (kg)", names="Category", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

# Map Visualization
st.subheader("Environmental Impact Map")
try:
    coords = get_coordinates(location)
    m = folium.Map(location=coords, zoom_start=10)
    
    # Add markers (example data)
    folium.Marker(
        coords,
        tooltip=f"Your Location: {location}",
        icon=folium.Icon(color="green")
    ).add_to(m)
    
    # Add pollution hotspots (mock data)
    for i in range(3):
        folium.Marker(
            [coords[0] + np.random.uniform(-0.1, 0.1), 
             coords[1] + np.random.uniform(-0.1, 0.1)],
            tooltip="Pollution Hotspot",
            icon=folium.Icon(color="red")
        ).add_to(m)
    
    folium_static(m, width=800)
except Exception as e:
    st.warning(f"Map could not be loaded: {str(e)}")

# Data Export
st.download_button(
    label="📥 Download Your Impact Report",
    data=df.to_csv(index=False),
    file_name="environmental_impact.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.caption("♻️ Sustainable AI App | v1.0")
