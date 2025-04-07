import streamlit as st
import matplotlib.pyplot as plt
import openai

# ------------------ CONFIG ------------------ #
st.set_page_config(page_title="Eco Impact Tracker 🌱", layout="centered")

# Use Streamlit secrets to hide API key (for Streamlit Cloud deployment)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ------------------ EMISSION FACTORS ------------------ #
EMISSION_FACTORS = {
    "electricity": 0.5,      # per kWh
    "travel": 0.21,          # per km
    "meat_meals": 2.5,       # per meal
    "water": 0.001,          # per liter
    "gas": 2.98              # per kg
}

# ------------------ FUNCTIONS ------------------ #
def calculate_emission(data):
    emissions = {
        "Electricity": data["electricity"] * EMISSION_FACTORS["electricity"],
        "Travel": data["travel"] * EMISSION_FACTORS["travel"],
        "Meat Meals": data["meat_meals"] * EMISSION_FACTORS["meat_meals"],
        "Water": data["water"] * EMISSION_FACTORS["water"],
        "Gas": data["gas"] * EMISSION_FACTORS["gas"],
    }
    total = sum(emissions.values())
    return emissions, total

def ask_bot(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in reducing carbon footprint and suggesting eco-friendly habits."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ------------------ UI ------------------ #
st.title("🌍 AI-based Environmental Impact Tracker")
st.markdown("Track your **weekly** carbon emissions and get AI-powered suggestions to reduce your footprint.")

# --- Input Section ---
with st.form("impact_form"):
    electricity = st.number_input("🔌 Electricity used (kWh)", min_value=0.0, value=0.0)
    travel = st.number_input("🚗 Travel distance (km)", min_value=0.0, value=0.0)
    meat_meals = st.number_input("🍖 Meat-based meals", min_value=0, value=0)
    water = st.number_input("🚿 Water used (liters)", min_value=0.0, value=0.0)
    gas = st.number_input("🔥 Gas used (kg)", min_value=0.0, value=0.0)
    submitted = st.form_submit_button("Calculate Impact")

if submitted:
    user_data = {
        "electricity": electricity,
        "travel": travel,
        "meat_meals": meat_meals,
        "water": water,
        "gas": gas
    }

    emissions, total = calculate_emission(user_data)

    st.success(f"✅ Your Total Weekly Carbon Emission: **{total:.2f} kg CO₂**")

    # --- Pie Chart ---
    fig, ax = plt.subplots()
    ax.pie(emissions.values(), labels=emissions.keys(), autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # --- AI Suggestions ---
    st.markdown("### 💡 Suggestions to Reduce Emissions")
    max_category = max(emissions, key=emissions.get)
    suggestions = {
        "Travel": "Try using public transport, carpooling, or biking for short trips.",
        "Meat Meals": "Replace meat meals with plant-based options at least twice a week.",
        "Electricity": "Turn off unused devices, switch to LED lights, and use efficient appliances.",
        "Gas": "Opt for electric or induction cooking methods.",
        "Water": "Use low-flow taps and fix leaks to save water."
    }
    st.info(f"Top source of emission: **{max_category}**\n\n{suggestions[max_category]}")

# ------------------ CHATBOT SECTION ------------------ #
st.divider()
st.markdown("## 🤖 Chat with EcoBot")
st.markdown("Ask anything related to your environmental impact, tips to go green, or sustainability.")

user_input = st.text_input("💬 Ask EcoBot:")

if user_input:
    with st.spinner("EcoBot is thinking..."):
        bot_reply = ask_bot(user_input)
        st.success(bot_reply)
