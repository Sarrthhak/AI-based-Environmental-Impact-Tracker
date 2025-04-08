# eco_tracker.py
import streamlit as st
import openai
import pandas as pd

# Initialize OpenAI (you'll add your key later)
openai.api_key = st.secrets["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"]

# Sample data
activities = [
    {"name": "Bike to work", "completed": True, "impact": 3.2},
    {"name": "Meat-free day", "completed": True, "impact": 2.5},
    {"name": "Recycle waste", "completed": False, "impact": 1.0}
]

# AI Suggestion Generator
def get_ai_suggestions(user_activities):
    prompt = f"""
    Generate 3 personalized eco-suggestions based on these activities: 
    {user_activities}. 
    Format as: Suggestion|Impact Level|Category
    Example: Use reusable bags|High|Waste
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return [s.split('|') for s in response.choices[0].message.content.split('\n')]

# Main App
st.title("🌱 Eco Activity Tracker")

# Activity Tracker
st.header("Your Activities")
for i, activity in enumerate(activities):
    col1, col2 = st.columns([3,1])
    with col1:
        st.checkbox(activity["name"], value=activity["completed"], key=f"activity_{i}")
    with col2:
        st.metric("CO₂ Saved", f"{activity['impact']} kg")

# AI Suggestions
if st.button("Get AI Suggestions"):
    suggestions = get_ai_suggestions([a["name"] for a in activities])
    st.header("🤖 AI Recommendations")
    for title, impact, category in suggestions:
        with st.expander(f"{title} ({category})"):
            st.write(f"Impact: {impact}")
            if st.button("Apply", key=title):
                activities.append({"name": title, "completed": False, "impact": 0})
                st.success("Added to your activities!")

# Add New Activity
with st.form("new_activity"):
    st.text_input("Activity Name", key="new_name")
    st.number_input("CO₂ Impact (kg)", key="new_impact")
    if st.form_submit_button("Add Activity"):
        activities.append({
            "name": st.session_state.new_name,
            "completed": False,
            "impact": st.session_state.new_impact
        })
