import streamlit as st
import openai
import os

# Set your OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit UI
st.set_page_config(page_title="EcoBot 🌿", page_icon="🌍")
st.title("🌿 AI Environmental Impact Tracker")
st.write("Ask me about your carbon footprint, eco-friendly habits, or how to reduce environmental impact.")

# Text input
user_input = st.text_input("💬 Enter your question:")

# OpenAI call
def get_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=[
            {"role": "system", "content": "You are a helpful assistant that gives advice on reducing environmental impact, energy saving, and sustainable living."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Display response
if user_input:
    with st.spinner("Thinking..."):
        reply = get_response(user_input)
        st.success(reply)
