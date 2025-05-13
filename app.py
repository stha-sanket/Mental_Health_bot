import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# Custom Modules
from utils.gemini_helper import get_ai_response
from utils.gemini_sentiment import analyze_sentiment
from utils.mood_tracker import save_mood, get_mood_history, display_mood_chart
from utils.breathing_exercise import breathing_exercise

# Page Configuration
st.set_page_config(
    page_title="Mindful Companion - Mental Health Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS for consistent font and margin
st.markdown("""
    <style>
    body, .stApp {
        font-family: 'Segoe UI', sans-serif;
    }
    .sidebar .sidebar-content {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm Mindful Companion, your mental health chat assistant. How are you feeling today?"}]

if 'mood_logged_today' not in st.session_state:
    st.session_state.mood_logged_today = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = "chat"

# Sidebar Navigation
def set_page(page_name):
    st.session_state.current_page = page_name

with st.sidebar:
    st.image("assets/brain.svg", width=60)
    st.markdown("## Mindful Companion")
    
    nav_options = {
        "💬 Chat": "chat",
        "🧘 Breathing": "breathing",
        "📊 Mood Tracker": "mood_tracker",
        "ℹ️ About": "about"
    }
    
    for label, key in nav_options.items():
        if st.button(label, use_container_width=True):
            set_page(key)

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "**Disclaimer**: This chatbot is not a replacement for professional mental health care. "
        "If you're in crisis, contact a professional or a local helpline immediately."
    )

# Pages
if st.session_state.current_page == "chat":
    st.title("💬 Chat with Mindful Companion")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        sentiment = analyze_sentiment(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response = get_ai_response(st.session_state.messages, sentiment)
            st.session_state.messages.append({"role": "assistant", "content": response})
            message_placeholder.write(response)

elif st.session_state.current_page == "breathing":
    st.title("🧘 Guided Breathing Exercise")
    st.write("Let's take a moment to focus on your breath and relax...")
    breathing_exercise()

elif st.session_state.current_page == "mood_tracker":
    st.title("📊 Mood Tracker")

    tab1, tab2 = st.tabs(["📝 Log Mood", "📈 Mood History"])

    with tab1:
        st.subheader("How are you feeling today?")
        mood_options = {
            "Very Happy 😄": 5,
            "Happy 🙂": 4,
            "Neutral 😐": 3,
            "Sad 😔": 2,
            "Very Sad 😢": 1
        }
        selected_mood = st.selectbox("Choose your current mood", options=list(mood_options.keys()), index=2)
        notes = st.text_area("Optional Notes", placeholder="Share your thoughts...")
        if st.button("💾 Save Mood"):
            score = mood_options[selected_mood]
            label = selected_mood.split()[0].lower()
            save_mood(score, label, notes)
            st.session_state.mood_logged_today = True
            st.success("Mood saved!")
            time.sleep(1)
            st.rerun()

    with tab2:
        mood_data = get_mood_history()
        if mood_data is not None and not mood_data.empty:
            display_mood_chart(mood_data)
        else:
            st.info("No mood history yet. Start logging to see patterns.")

elif st.session_state.current_page == "about":
    st.title("ℹ️ About Mindful Companion")
    st.markdown("""
    ### Welcome to Mindful Companion  
    Your AI-powered mental wellness buddy – built to help you reflect, relax, and grow 🌿

    #### 💡 Features
    - **Smart Chat:** AI-driven responses for mental clarity
    - **Breathing Guide:** Easy-to-follow calming exercises
    - **Mood Tracker:** Stay aware of your emotional patterns

    #### 🔒 Privacy First
    All data is stored locally and never shared. Your emotional health is your own.

    #### 🚨 Help in Crisis
    - **Suicide Prevention (US):** 988 or 1-800-273-8255
    - **Text Line:** HOME to 741741
    - **Emergency:** Dial your local helpline

    ---
    """)

    st.subheader("🧹 Data Management")
    if st.button("Delete All My Data"):
        try:
            st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm Mindful Companion, your mental health chat assistant. How are you feeling today?"}]
            st.session_state.mood_logged_today = False
            if os.path.exists("mood_data.csv"):
                os.remove("mood_data.csv")
            st.success("Your data has been cleared!")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
