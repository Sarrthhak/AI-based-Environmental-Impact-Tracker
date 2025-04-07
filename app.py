import streamlit as st
import openai

# Initialize OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Bot response logic ---
def get_bot_response(user_input):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an eco-friendly assistant helping users reduce their environmental impact."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )
    return response.choices[0].message.content


# --- Streamlit App UI ---
st.set_page_config(page_title="Environmental Impact Tracker", page_icon="🌱")

st.title("🌍 AI-Based Environmental Impact Tracker")
st.markdown("Track your weekly resource usage and get eco-friendly suggestions!")

st.subheader("📊 Weekly Resource Usage Input")

# Input fields
water = st.number_input("Water used (litres)", min_value=0)
electricity = st.number_input("Electricity consumed (kWh)", min_value=0)
plastic = st.number_input("Plastic waste generated (grams)", min_value=0)
transport = st.number_input("Distance travelled using fuel vehicles (km)", min_value=0)

if st.button("Calculate Impact"):
    st.subheader("🌿 Estimated Environmental Impact")

    # Basic logic
    impact_score = 0
    if water > 500:
        st.warning("💧 High water usage. Consider reducing it.")
        impact_score += 1
    if electricity > 20:
        st.warning("⚡ Try reducing electricity consumption.")
        impact_score += 1
    if plastic > 1000:
        st.warning("♻️ Too much plastic waste! Try reusing or recycling.")
        impact_score += 1
    if transport > 50:
        st.warning("🚗 Consider using bicycles or public transport more often.")
        impact_score += 1

    if impact_score == 0:
        st.success("✅ Great job! You're living sustainably. 🌱")
    elif impact_score <= 2:
        st.info("👍 You're doing okay. A few improvements can make a big difference.")
    else:
        st.error("⚠️ Let's work on reducing your environmental impact.")

st.markdown("---")
st.subheader("💬 Ask the EcoBot")

# Chatbot UI
user_input = st.text_input("Type your question (e.g., How to reduce water usage?)")

if user_input:
    with st.spinner("Thinking..."):
        bot_reply = get_bot_response(user_input)
    st.markdown(f"**EcoBot:** {bot_reply}")
