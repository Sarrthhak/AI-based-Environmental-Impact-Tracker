import os
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in your .env file.")
    st.stop()

# Configure Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

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
        background-color: #e3f2fd !important;  /* Light blue for contrast */
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

# ====== App Configuration ======
st.set_page_config(
    page_title="🌿 Personal Environmental Impact Tracker", 
    layout="centered",
    page_icon="🌍",
    initial_sidebar_state="expanded"
)

# Header with logo-like styling
st.markdown(
    """
    <div style="background-color: #2e8b57; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; text-align: center; margin: 0;">🌱 Personal Environmental Impact Tracker</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("Track your daily activities and learn how to reduce your carbon footprint!")

# ====== Session State Initialization ======
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.activities = []
    st.session_state.total_footprint = 0.0
    st.session_state.first_interaction = True

# ====== Chat Display ======
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ====== Initial Greeting ======
if st.session_state.first_interaction:
    welcome = """
    Hi there! 🌍 I'm your eco-assistant. Tell me about your daily activities and I'll calculate your carbon footprint.
    
    **Examples:**
    - 🚗 "I drove 15 km to work in a petrol car"
    - 🍔 "Ate a beef burger for lunch"
    - ❄️ "Used my AC for 4 hours"
    - 🚌 "Took the bus for 10 km"
    """
    st.session_state.chat_history.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)
    st.session_state.first_interaction = False

# ====== User Input & Processing ======
user_input = st.chat_input("Describe your activity (e.g., 'I drove 10 km')")

if user_input:
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Check if user is done
    if any(phrase in user_input.lower() for phrase in ["that's all", "that is all", "thats all", "nothing else"]):
        # Generate summary
        summary_prompt = f"""
        The user reported these activities today:
        {st.session_state.activities}
        
        Total estimated carbon footprint: {st.session_state.total_footprint:.2f} kg CO2.
        
        Provide a friendly summary with:
        1. Environmental impact assessment:
           - < 5 kg → "Great job! 🌿"
           - 5-15 kg → "Average impact 🌍"
           - > 15 kg → "High impact ⚠️"
        2. Two personalized suggestions for improvement
        3. An encouraging closing remark
        
        Keep it concise (3-4 sentences max) and motivational!
        """
        
        with st.chat_message("assistant"):
            with st.spinner("🌱 Calculating your daily impact..."):
                try:
                    response = model.generate_content(summary_prompt)
                    summary = response.text
                    
                    # Display summary
                    st.markdown(summary)
                    
                    # Add visual feedback
                    if st.session_state.total_footprint < 5:
                        st.balloons()
                    elif st.session_state.total_footprint > 15:
                        st.warning("Consider these reduction tips!")
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": summary})
                except Exception as e:
                    error_msg = f"⚠️ Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    else:
        # Process individual activity
        prompt = f"""
        You're an environmental scientist calculating carbon footprints. The user said:
        "{user_input}"
        
        Follow these steps:
        1. Identify the activity type (transport, food, energy, etc.)
        2. Extract key details (distance, vehicle type, food type, duration)
        3. Calculate CO2 emissions using these benchmarks:
           - Petrol car: 0.23 kg/km
           - Diesel car: 0.20 kg/km
           - Electric car: 0.05 kg/km (varies by grid)
           - Beef: 2.5 kg per serving
           - AC: 0.6 kg per hour
        4. Format response as:
           "Your [activity] → [X] kg CO2. [Impact level: 🌿/⚠️/🔴]
           Tip: [Personalized suggestion]"
        
        If information is missing, ask ONE clarifying question.
        """
        
        with st.chat_message("assistant"):
            with st.spinner("🌍 Analyzing your activity..."):
                try:
                    response = model.generate_content(prompt)
                    reply = response.text
                    
                    # Extract footprint from response
                    footprint_match = re.search(r'(\d+\.?\d*)\s*kg\s*CO2', reply)
                    if footprint_match:
                        footprint = float(footprint_match.group(1))
                        st.session_state.total_footprint += footprint
                        st.session_state.activities.append({
                            "activity": user_input, 
                            "footprint": footprint
                        })
                    
                    # Display response
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    
                except Exception as e:
                    error_msg = f"⚠️ Sorry, I couldn't process that: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# ====== Sidebar ======
with st.sidebar:
    st.markdown(
        """
        <div style="background-color: #2e8b57; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
            <h3 style="color: white; text-align: center;">📊 Today's Summary</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.session_state.activities:
        # Card-style metric
        st.markdown(
            f"""
            <div style="background-color: white; border: 1px solid #2e8b57; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                <h4 style="color: #1b5e20; margin-top: 0;">Total Carbon Footprint</h4>
                <h2 style="color: #2e8b57; text-align: center; margin: 0;">{st.session_state.total_footprint:.2f} kg CO2</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.write("**Activities logged:**")
        for activity in st.session_state.activities:
            st.markdown(
                f"""
                <div style="background-color: #e8f5e9; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;">
                    <p style="margin: 0;">{activity['activity']}: <strong>{activity['footprint']:.2f} kg</strong></p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No activities logged yet")
    
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()
