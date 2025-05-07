import os
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import google.generativeai as genai
import streamlit as st
import re

# Try to use NLTK if available, otherwise will fallback to Gemini
try:
    # Download NLTK data if not already present
    nltk.download('vader_lexicon', quiet=True)
    sia = SentimentIntensityAnalyzer()
    NLTK_AVAILABLE = True
except:
    NLTK_AVAILABLE = False

# Gemini API key
API_KEY = os.environ.get("GEMINI_API_KEY", "")

def setup_gemini():
    """Setup the Gemini API with the provided key"""
    if API_KEY:
        genai.configure(api_key=API_KEY)
        return True
    return False

def analyze_sentiment(text):
    """
    Analyze the sentiment of the provided text.
    Uses NLTK as primary method and Gemini as fallback.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentiment score, label, and confidence
    """
    # First try with NLTK if available (faster and doesn't use API quota)
    if NLTK_AVAILABLE:
        try:
            scores = sia.polarity_scores(text)
            
            # Convert compound score to 1-5 scale
            # NLTK compound ranges from -1 to 1
            sentiment_score = int((scores['compound'] + 1) * 2.5) + 1
            
            # Limit to valid range
            sentiment_score = max(1, min(5, sentiment_score))
            
            # Determine label
            if sentiment_score >= 4:
                sentiment_label = "happy"
            elif sentiment_score == 3:
                sentiment_label = "neutral"
            else:
                sentiment_label = "sad"
                
            # Calculate confidence from subjectivity
            confidence = abs(scores['compound'])
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'confidence': confidence
            }
            
        except Exception as e:
            st.error(f"NLTK sentiment analysis error: {str(e)}")
            # If NLTK fails, continue to Gemini method if available
            pass
    
    # Fallback to Gemini if NLTK is unavailable or failed
    if setup_gemini():
        try:
            # Configure the model
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Create a simpler prompt for sentiment analysis
            prompt = """Analyze the sentiment of the following text. Rate it on a scale of 1 to 5, where:
            1 = Very negative
            2 = Negative
            3 = Neutral
            4 = Positive
            5 = Very positive
            
            Also provide a confidence score between 0 and 1, and one of these labels: happy, neutral, sad.
            
            Text to analyze: "{text}"
            
            Respond with this format (no need for JSON):
            Sentiment score: [number 1-5]
            Sentiment label: [happy/neutral/sad]
            Confidence: [number between 0-1]
            """
            
            response = model.generate_content(prompt.format(text=text))
            response_text = response.text
            
            # Parse the response using regex
            score_match = re.search(r'Sentiment score: (\d+)', response_text)
            label_match = re.search(r'Sentiment label: (\w+)', response_text)
            conf_match = re.search(r'Confidence: (0\.\d+|1\.0|1)', response_text)
            
            if score_match and label_match and conf_match:
                sentiment_score = int(score_match.group(1))
                sentiment_label = label_match.group(1).lower()
                confidence = float(conf_match.group(1))
                
                # Ensure values are within allowed ranges
                sentiment_score = max(1, min(5, sentiment_score))
                confidence = max(0, min(1, confidence))
                
                return {
                    'sentiment_score': sentiment_score,
                    'sentiment_label': sentiment_label,
                    'confidence': confidence
                }
            else:
                # If we can't parse the response correctly, use basic heuristics
                if 'positive' in response_text.lower():
                    return {'sentiment_score': 4, 'sentiment_label': 'happy', 'confidence': 0.7}
                elif 'negative' in response_text.lower():
                    return {'sentiment_score': 2, 'sentiment_label': 'sad', 'confidence': 0.7}
                else:
                    return {'sentiment_score': 3, 'sentiment_label': 'neutral', 'confidence': 0.5}
                
        except Exception as e:
            st.error(f"Gemini sentiment analysis error: {str(e)}")
            # If Gemini fails or is unavailable, return a neutral default
            pass
    
    # Default neutral sentiment if all methods fail
    return {
        'sentiment_score': 3,
        'sentiment_label': 'neutral',
        'confidence': 0.1  # Low confidence since this is a default
    }