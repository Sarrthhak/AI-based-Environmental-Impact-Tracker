import streamlit as st
import os
import sys

# --- Initial Setup ---
st.set_page_config(page_title="🌱 Eco Tracker", page_icon="🌍")

# --- Package Installation Check ---
try:
    import openai
    import pandas as pd
except ImportError:
    st.error("""
    Missing required packages. Please ensure your requirements.txt contains:
    streamlit, openai, pandas
    """)
    if st.button("Attempt Auto-install (may require redeploy)"):
        os.system(f"{sys.executable} -m pip install openai pandas")
        st.rerun()
    st.stop()

# --- Secure API Key Loading ---
def load_api_key():
    # Try all possible key locations
    key = (
        st.secrets.get("OPENAI_KEY") or          # Streamlit Cloud secrets
        os.environ.get("OPENAI_KEY") or          # Environment variables
        st.session_state.get("temp_key")         # Temporary user input
    )
    
    if not key:
        with st.sidebar:
            st.warning("API key not configured")
            temp_key = st.text_input(
                "Enter OpenAI Key (temporary)", 
                type="password",
                help="For testing only - configure secrets for production"
            )
            if temp_key:
                st.session_state.temp_key = temp_key
                st.rerun()
        st.stop()
    return key

openai.api_key = load_api_key()

# --- Main App ---
def main():
    st.title("🌍 Eco Activity Tracker")
    
    # Sample data storage
    if 'activities' not in st.session_state:
        st.session_state.activities = [
            {"name": "Bike to work", "completed": True, "impact": 3.2},
            {"name": "Meat-free day", "completed": False, "impact": 2.5}
        ]
    
    # Activity List
    st.header("Your Activities")
    for i, activity in enumerate(st.session_state.activities):
        cols = st.columns([3, 1, 1])
        with cols[0]:
            st.checkbox(
                activity["name"],
                value=activity["completed"],
                key=f"activity_{i}",
                on_change=lambda i=i: toggle_activity(i)
            )
        with cols[1]:
            st.metric("CO₂ Saved", f"{activity['impact']} kg")
    
    # Add New Activity
    with st.expander("➕ Add New Activity"):
        with st.form("new_activity"):
            name = st.text_input("Activity Name")
            impact = st.number_input("CO₂ Impact (kg)", min_value=0.0, step=0.1)
            if st.form_submit_button("Add"):
                st.session_state.activities.append({
                    "name": name,
                    "completed": False,
                    "impact": impact
                })
                st.rerun()

def toggle_activity(index):
    st.session_state.activities[index]["completed"] = not st.session_state.activities[index]["completed"]

if __name__ == "__main__":
    main()
