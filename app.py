import os
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# ====== MUST BE FIRST STREAMLIT COMMAND ======
st.set_page_config(
    page_title="🌿 Personal Environmental Impact Tracker", 
    layout="centered",
    page_icon="🌍",
    initial_sidebar_state="expanded"
)

# ====== Custom CSS for Green Theme ======
st.markdown(
    """
    <style>
    :root {
        --primary-green: #2e8b57;
        --secondary-green: #3cb371;
        --light-green: #e8f5e9;
        --dark-green: #1b5e20;
    }
    
    /* Main background */
    .stApp {
        background-color: #f5fef5;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--light-green) !important;
        border-right: 1px solid var(--primary-green);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--dark-green) !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--primary-green) !important;
        color: white !important;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: var(--dark-green) !important;
    }
    
    /* Chat bubbles */
    .stChatMessage {
        border-radius: 12px !important;
        padding: 12px !important;
    }
    
    /* User message bubble */
    [data-testid="user"] {
        background-color: #e3f2fd !important;
    }
    
    /* Assistant message bubble */
    [data-testid="assistant"] {
        background-color: var(--light-green) !important;
        border-left: 3px solid var(--primary-green) !important;
    }
    
    /* Metric cards */
    .stMetric {
        background-color: white;
        border: 1px solid var(--primary-green);
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Input box */
    .stTextInput>div>div>input {
        border: 1px solid var(--primary-green) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ====== Load Config ======
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in your .env file.")
    st.stop()

# Configure Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# ====== App Header ======
st.markdown(
    """
    <div style="background-color: #2e8b57; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; text-align: center; margin: 0;">🌱 Personal Environmental Impact Tracker</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("Track your daily activities and learn how to reduce your carbon footprint!")

# ====== Rest of your code (unchanged) ======
# [Keep all your existing session state, chat logic, and sidebar code below]
# Initialize session state, chat display, etc. (same as before)
