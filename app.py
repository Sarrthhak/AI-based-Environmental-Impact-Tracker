import os
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
st.write("RAW SECRETS DUMP:", st.secrets)  # Nuclear verification

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success(f"✅ Key loaded: {api_key[:4]}...{api_key[-4:]}")
except Exception as e:
    st.error(f"""
    ❌ CRITICAL ERROR: {str(e)}
    Verify:
    1. Secret name is EXACTLY 'GEMINI_API_KEY' (case-sensitive)
    2. You clicked 'Save' after editing secrets
    3. You redeployed after saving
    """)
    st.stop()

# Configure Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# App configuration
st.set_page_config(
    page_title="🌿 Personal Environmental Impact Tracker", 
    layout="centered",
    page_icon="🌍"
)
st.title("🌱 Personal Environmental Impact Tracker")
st.caption("Track your daily activities and learn how to reduce your carbon footprint!")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.activities = []
    st.session_state.total_footprint = 0.0
    st.session_state.first_interaction = True

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Initial assistant greeting
if st.session_state.first_interaction:
    welcome = """
    Hi there! 🌍 I'm your eco-assistant. Tell me about your daily activities and I'll calculate your carbon footprint.
    
    **Examples:**
    - "I drove 15 km to work in a petrol car"
    - "Ate a beef burger for lunch"
    - "Used my AC for 4 hours"
    - "Took the bus for 10 km"
    """
    st.session_state.chat_history.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)
    st.session_state.first_interaction = False

# Chat input
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
            with st.spinner("Calculating your daily impact..."):
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
            with st.spinner("Analyzing your activity..."):
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

# Sidebar with summary
with st.sidebar:
    st.subheader("Today's Summary")
    if st.session_state.activities:
        st.metric("Total Footprint", f"{st.session_state.total_footprint:.2f} kg CO2")
        st.write("**Activities logged:**")
        for activity in st.session_state.activities:
            st.write(f"- {activity['activity']}: {activity['footprint']:.2f} kg")
    else:
        st.write("No activities logged yet")
    
    st.button("Reset Session", on_click=lambda: st.session_state.clear())
