import os
import google.generativeai as genai
import streamlit as st

# Initialize Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = "gemini-1.5-pro"  # Using Gemini 1.5 Pro model

def setup_gemini():
    """Setup the Gemini API with the provided key"""
    if API_KEY:
        genai.configure(api_key=API_KEY)
        return True
    return False

def get_ai_response(messages, sentiment=None):
    """
    Get a response from the Gemini API based on the conversation history.
    Adjusts the system message based on detected sentiment.
    
    Args:
        messages: List of message dictionaries (role, content)
        sentiment: Dictionary containing sentiment analysis results
        
    Returns:
        String response from the AI
    """
    try:
        # Check if API key is available and configure
        if not setup_gemini():
            return "⚠️ Gemini API key is missing. Please set the GEMINI_API_KEY environment variable to enable the AI chatbot."
        
        # Create an appropriate system message based on sentiment
        system_message = """You are Mindful Companion, a supportive and empathetic mental health chatbot.
Your primary goal is to provide emotional support, compassion, and helpful mental wellness strategies.

Guidelines:
- Respond with warmth, empathy, and a calm, supportive tone
- Keep responses concise (3-5 sentences maximum) and conversational
- Provide practical mental wellness suggestions when appropriate
- Suggest the breathing exercise feature when users seem stressed or anxious
- Recommend the mood tracker for emotional awareness
- NEVER claim to be a therapist, doctor, or medical professional
- If user mentions serious mental health crisis, self-harm, or suicide, acknowledge the severity and
  suggest professional help resources like crisis hotlines (988)

Remember that you are a supportive companion, not a replacement for professional mental health care."""
        
        # If strong negative emotion is detected, enhance empathy in system prompt
        if sentiment and sentiment.get('sentiment_score', 3) <= 2 and sentiment.get('confidence', 0) > 0.7:
            system_message += """

This user appears to be experiencing difficult emotions. Prioritize empathy, validation, 
and emotional support in your response. Use a gentle tone and avoid offering solutions too quickly
before acknowledging their feelings."""
        
        # Create prompt with conversation history
        prompt = system_message + "\n\nConversation History:\n"
        
        # Add the conversation messages (skipping initial assistant greeting if present)
        for message in messages:
            if not (message["role"] == "assistant" and messages.index(message) == 0):
                role = "User" if message["role"] == "user" else "Assistant"
                prompt += f"{role}: {message['content']}\n"
        
        # Add final instruction for the AI to respond
        prompt += "\nAssistant:"
        
        # Create a Gemini model and generate content
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}. Please try again."