import os
from openai import OpenAI
import streamlit as st

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=api_key)

def get_ai_response(messages, sentiment=None):
    """
    Get a response from the OpenAI API based on the conversation history.
    Adjusts the system message based on detected sentiment.
    
    Args:
        messages: List of message dictionaries (role, content)
        sentiment: Dictionary containing sentiment analysis results
        
    Returns:
        String response from the AI
    """
    try:
        # Check if API key is available
        if not api_key:
            return "⚠️ OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable to enable the AI chatbot."
        
        # Prepare the conversation history for the API call
        conversation = []
        
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
        
        # Add system message
        conversation.append({"role": "system", "content": system_message})
        
        # Add user messages, filtering out the initial assistant greeting
        for message in messages:
            if not (message["role"] == "assistant" and messages.index(message) == 0):
                conversation.append({"role": message["role"], "content": message["content"]})
        
        # Make the API call
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation,
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}. Please try again."
