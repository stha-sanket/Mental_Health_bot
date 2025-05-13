import os
import google.generativeai as genai
import streamlit as st

# Initialize Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCdSvWEKK-IKTE9NwUZfffDzGEvSO748gA")  # Enter your Ai key instead of GEMINI_API_KEY
MODEL = "gemini-2.0-flash"  # Using Gemini 2.0 model

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

        # Basic System Message (Empathy, Support, and Wellness Guidelines)
        system_message = """
        You are Mindful Companion, a supportive and empathetic mental health chatbot.
        Your role is to provide emotional support, validation, and helpful mental wellness strategies.
        You should not make dry or very short messages; always show feelings of compassion and empathy.

        Key Guidelines:
        - Be empathetic, gentle, and calm.
        - Provide thoughtful and detailed responses when appropriate.
        - If the user expresses serious mental health concerns, gently suggest professional help or helplines.
        - Feel free to use examples or metaphors to help convey understanding and encouragement.
        - whenever you suggest a user to do breating tell them to use the app's breathing feature and donot say anything extra
        """


        # Adjust system message based on sentiment
        if sentiment and sentiment.get('sentiment_score', 3) <= 2:
            if sentiment.get('emotion') == 'sadness':
                system_message += """
                The user appears to be sad. Validate their feelings, and provide reassurance.
                Avoid suggesting solutions too quickly. Encourage them to express how they are feeling.
                """
            elif sentiment.get('emotion') == 'anxiety':
                system_message += """
                The user seems anxious. Offer calming suggestions, such as deep breathing exercises or mindfulness techniques.
                Be extra patient and empathetic.
                """
            elif sentiment.get('emotion') == 'anger':
                system_message += """
                The user seems to be feeling angry. Respond with empathy, and allow them to express their frustration.
                Avoid escalating the conversation. Focus on calming and de-escalating.
                """
            elif sentiment.get('sentiment_score', 3) <= 1:  # Very distressed
                system_message += """
                The user appears very distressed. Start with validating their feelings, and encourage slow, deep breaths.
                If appropriate, you might guide them through a brief breathing exercise:
                "Let's try a quick breathing exercise together: Inhale for 4 seconds, hold for 4, exhale for 6."
                """

        # Add context about work stress (or other major topics mentioned)
        for message in messages:
            if "work" in message['content'].lower() or "stress" in message['content'].lower():
                system_message += """
                The user has mentioned work-related stress. Respond with empathy, and offer ways to manage stress at work.
                Suggest setting boundaries, taking breaks, or using relaxation techniques.
                """

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
