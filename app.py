import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import folium
from streamlit_folium import folium_static
import pickle
import os

# ======================
# CONFIGURATION
# ======================
st.set_page_config(
    page_title="AI Environmental Impact Tracker",
    page_icon="🌍",
    layout="wide"
)

# Load secrets (API keys)
WEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")

# ======================
# CACHED FUNCTIONS
# ======================
@st.cache_data
def load_model():
    """Load pre-trained AI model"""
    try:
        # Replace with your actual model file
        # model = pickle.load(open('model.pkl', 'rb'))
        # Mock model for demo:
        X = np.random.rand(100, 3) * 100
        y = X.sum(axis=1) * 10
        return RandomForestRegressor().fit(X, y)
    except Exception as e:
        st.error(f"Model loading failed: {e}")
        return None

# ======================
# SIDEBAR INPUTS
# ======================
with st.sidebar:
    st.header("🌱 Your Carbon Profile")
    
    # Activity Inputs
    transport_type = st.selectbox(
        "Transport Mode",
        ["Car", "Bus", "Train", "Bicycle"]
    )
    distance_km = st.slider("Daily Distance (km)", 0, 200, 10)
    
    # Energy Inputs
    energy_kwh = st.number_input("Monthly Energy (kWh)", min_value=0, value=200)
    
    # Advanced
    with st.expander("Advanced Settings"):
        diet_type = st.selectbox(
            "Diet Preference",
            ["Omnivore", "Vegetarian", "Vegan"]
        )

# ======================
# AI PREDICTION ENGINE
# ======================
def predict_impact(model, inputs):
    """Run AI prediction with user inputs"""
    try:
        # Convert inputs to model format
        diet_map = {"Omnivore": 2, "Vegetarian": 1, "Vegan": 0}
        transport_map = {"Car": 3, "Bus": 2, "Train": 1, "Bicycle": 0}
        
        features = np.array([[
            distance_km,
            energy_kwh,
            diet_map[inputs['diet']],
            transport_map[inputs['transport']]
        ]])
        
        return model.predict(features)[0]
    except Exception as e:
        st.error(f"Prediction failed: {e}")
        return 0.0

# ======================
# MAIN DASHBOARD
# ======================
model = load_model()

# Header
st.title("🌍 AI Environmental Impact Tracker")
st.markdown("""Track your carbon footprint with AI-powered insights""")

# Prediction Card
col1, col2 = st.columns(2)
with col1:
    if model:
        prediction = predict_impact(model, {
            "diet": diet_type,
            "transport": transport_type
        })
        
        st.metric(
            label="Estimated Annual CO₂ Impact",
            value=f"{prediction:.2f} kg",
            delta="-5% vs average" if prediction < 1500 else "+10% vs average"
        )
        
        # Recommendations
        if prediction > 2000:
            st.error("🚨 High Impact! Try reducing car usage.")
        elif prediction > 1500:
            st.warning("⚠️ Moderate Impact. Consider plant-based diet options.")
        else:
            st.success("✅ Sustainable Lifestyle!")

# Visualization
with col2:
    impact_data = pd.DataFrame({
        "Category": ["Transport", "Energy", "Diet"],
        "Impact": [
            distance_km * (0.5 if transport_type == "Car" else 0.2),
            energy_kwh * 0.3,
            500 if diet_type == "Omnivore" else 200
        ]
    })
    
    fig = px.pie(
        impact_data,
        values="Impact",
        names="Category",
        hole=0.3,
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    st.plotly_chart(fig, use_container_width=True)

# ======================
# MAP VISUALIZATION
# ======================
if st.checkbox("Show Regional Impact Data"):
    st.subheader("Pollution Hotspots")
    
    # Example map centered on user's country
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # India default
    
    # Add markers (replace with real data)
    folium.Marker(
        location=[19.0760, 72.8777],  # Mumbai
        tooltip="High Emission Zone",
        icon=folium.Icon(color="red")
    ).add_to(m)
    
    folium_static(m, width=800)

# ======================
# DATA EXPORT
# ======================
st.download_button(
    label="📥 Download Your Report",
    data=impact_data.to_csv(index=False),
    file_name="environmental_impact_report.csv",
    mime="text/csv"
)

# ======================
# FOOTER
# ======================
st.markdown("---")
st.caption("♻️ Made with Streamlit | AI Model v1.0")
