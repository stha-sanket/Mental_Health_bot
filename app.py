import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# Using Gemini instead of OpenAI
from utils.gemini_helper import get_ai_response
from utils.gemini_sentiment import analyze_sentiment
from utils.mood_tracker import save_mood, get_mood_history, display_mood_chart
from utils.breathing_exercise import breathing_exercise

# Page configuration
st.set_page_config(
    page_title="Mindful Companion - Mental Health Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Mindful Companion, your mental health chat assistant. How are you feeling today?"}
    ]

if 'mood_logged_today' not in st.session_state:
    st.session_state.mood_logged_today = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = "chat"

# Functions to change pages
def show_chat():
    st.session_state.current_page = "chat"

def show_breathing():
    st.session_state.current_page = "breathing"

def show_mood_tracker():
    st.session_state.current_page = "mood_tracker"

def show_about():
    st.session_state.current_page = "about"

# Sidebar navigation
st.sidebar.title("Mindful Companion")
st.sidebar.image("assets/brain.svg", width=50)

# Navigation buttons
st.sidebar.button("💬 Chat", on_click=show_chat, use_container_width=True)
st.sidebar.button("🧘 Breathing Exercise", on_click=show_breathing, use_container_width=True)
st.sidebar.button("📊 Mood Tracker", on_click=show_mood_tracker, use_container_width=True)
st.sidebar.button("ℹ️ About", on_click=show_about, use_container_width=True)

# Disclaimer in sidebar
st.sidebar.markdown("---")
st.sidebar.caption(
    "**Disclaimer**: This chatbot is not a replacement for professional mental health care. "
    "If you're experiencing a crisis, please contact a mental health professional or "
    "call a crisis helpline immediately."
)

# Chat page
if st.session_state.current_page == "chat":
    st.title("💬 Chat with Mindful Companion")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get sentiment of user message for mood tracking
        sentiment = analyze_sentiment(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Get AI response
            response = get_ai_response(st.session_state.messages, sentiment)
            
            # Add response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            message_placeholder.write(response)
            
        # Check if user hasn't logged mood today and sentiment indicates they're sharing feelings
        if not st.session_state.mood_logged_today and sentiment['confidence'] > 0.7:
            mood_score = sentiment['sentiment_score']
            mood_label = sentiment['sentiment_label']
            
            # Display a suggestion to log mood
            st.info(f"I notice you're feeling {mood_label}. Would you like to log this in your mood tracker?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, log my mood"):
                    save_mood(mood_score, mood_label)
                    st.session_state.mood_logged_today = True
                    st.success("Mood logged successfully!")
                    time.sleep(1)
                    st.rerun()
            with col2:
                if st.button("No, thanks"):
                    st.session_state.mood_logged_today = True
                    st.rerun()

# Breathing exercise page
elif st.session_state.current_page == "breathing":
    breathing_exercise()

# Mood tracker page
elif st.session_state.current_page == "mood_tracker":
    st.title("📊 Mood Tracker")
    
    # Sub-tabs for mood input and history
    tab1, tab2 = st.tabs(["Log Mood", "Mood History"])
    
    with tab1:
        st.subheader("How are you feeling today?")
        
        mood_options = {
            "Very Happy 😄": 5,
            "Happy 🙂": 4, 
            "Neutral 😐": 3,
            "Sad 😔": 2,
            "Very Sad 😢": 1
        }
        
        selected_mood = st.selectbox(
            "Select your mood",
            options=list(mood_options.keys()),
            index=2
        )
        
        mood_score = mood_options[selected_mood]
        mood_notes = st.text_area("Notes (optional)", placeholder="Any thoughts you'd like to capture...")
        
        if st.button("Save Mood"):
            save_mood(mood_score, selected_mood.split()[0].lower(), mood_notes)
            st.session_state.mood_logged_today = True
            st.success("Mood logged successfully!")
            time.sleep(1)
            st.rerun()
    
    with tab2:
        mood_data = get_mood_history()
        if mood_data is not None and not mood_data.empty:
            display_mood_chart(mood_data)
        else:
            st.info("You haven't logged any moods yet. Start tracking to see your mood patterns over time.")

# About page
elif st.session_state.current_page == "about":
    st.title("ℹ️ About Mindful Companion")
    
    st.write("""
    ## Welcome to Mindful Companion
    
    Mindful Companion is a supportive chatbot designed to help you navigate your feelings, 
    practice mindfulness, and track your emotional well-being. While I'm here to provide 
    support and companionship, I'm not a replacement for professional mental health care.
    
    ### Features
    
    - **Supportive Chat**: Have conversations about your feelings in a safe, non-judgmental space
    - **Guided Breathing**: Follow simple breathing exercises to help reduce stress and anxiety
    - **Mood Tracking**: Monitor your emotional well-being over time
    
    ### Privacy & Data
    
    Your privacy is important. Conversations and mood data are stored locally and not shared with 
    third parties. You can delete your data at any time.
    
    ### Resources
    
    If you're experiencing a mental health crisis or need immediate support, please contact:
    
    - **National Suicide Prevention Lifeline**: 988 or 1-800-273-8255
    - **Crisis Text Line**: Text HOME to 741741
    - **Emergency Services**: 911 (US) or your local emergency number
    """)
    
    # Provide option to clear data
    st.subheader("Data Management")
    if st.button("Clear All My Data"):
        # Reset session state
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm Mindful Companion, your mental health chat assistant. How are you feeling today?"}
        ]
        st.session_state.mood_logged_today = False
        
        # Delete mood data file if it exists
        try:
            if os.path.exists("mood_data.csv"):
                os.remove("mood_data.csv")
            st.success("All data cleared successfully!")
        except Exception as e:
            st.error(f"Error clearing data: {e}")
