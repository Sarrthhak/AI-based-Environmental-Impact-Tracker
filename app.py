import streamlit as st
import os
import sys
import json

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

def get_ai_suggestions(existing_activities):
    """Get personalized eco-tips from OpenAI"""
    try:
        prompt = f"""
        Suggest 3 new eco-friendly activities based on these existing ones: 
        {[a['name'] for a in existing_activities]}.
        For each suggestion, provide:
        - A short title (max 5 words)
        - Estimated CO₂ savings in kg (as number)
        - Difficulty level (Easy/Medium/Hard)
        
        Format as JSON: {{"suggestions": [{{"title": "...", "savings": x, "difficulty": "..."}}]}}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI suggestion failed: {str(e)}")
        return {"suggestions": []}

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

    # AI Suggestions Section
    st.header("🤖 AI Recommendations")
    if st.button("Get Personalized Tips"):
        with st.spinner("Analyzing your habits..."):
            ai_response = get_ai_suggestions(st.session_state.activities)
            
        for suggestion in ai_response["suggestions"]:
            with st.expander(f"✨ {suggestion['title']} ({suggestion['difficulty']})"):
                st.metric("Estimated Savings", f"{suggestion['savings']} kg CO₂")
                if st.button("Add This", key=suggestion["title"]):
                    st.session_state.activities.append({
                        "name": suggestion["title"],
                        "completed": False,
                        "impact": suggestion["savings"]
                    })
                    st.rerun()
        
    with st.expander("➕ Add New Activity"):
    with st.form("new_activity"):
        name = st.text_input("Activity Name (e.g. 'Use reusable bags')")
        
        # Let AI estimate impact if unknown
        if st.toggle("Calculate impact automatically"):
            with st.spinner("Estimating CO₂ impact..."):
                try:
                    prompt = f"Estimate CO₂ savings in kg (as number only) for: {name}"
                    impact = float(openai.Completion.create(
                        model="text-davinci-003",
                        prompt=prompt,
                        max_tokens=10
                    ).choices[0].text.strip())
                except:
                    impact = 0.0
        else:
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
