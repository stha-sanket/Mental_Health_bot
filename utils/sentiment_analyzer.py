import os
import json
from openai import OpenAI
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import streamlit as st

# Try to use NLTK if available, otherwise will fallback to OpenAI
try:
    # Download NLTK data if not already present
    nltk.download('vader_lexicon', quiet=True)
    sia = SentimentIntensityAnalyzer()
    NLTK_AVAILABLE = True
except:
    NLTK_AVAILABLE = False

# OpenAI client
api_key = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=api_key) if api_key else None

def analyze_sentiment(text):
    """
    Analyze the sentiment of the provided text.
    Uses NLTK as primary method and OpenAI as fallback.
    
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
            
        except Exception:
            # If NLTK fails, continue to OpenAI method if available
            pass
    
    # Fallback to OpenAI if NLTK is unavailable or failed
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. "
                        + "Analyze the sentiment of the text and rate it on a scale of 1 to 5, "
                        + "where 1 is very negative and 5 is very positive. "
                        + "Also provide a confidence score between 0 and 1, and a simple label (happy, neutral, sad). "
                        + "Respond with JSON in this format: "
                        + "{'sentiment_score': number, 'sentiment_label': string, 'confidence': number}"
                    },
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure values are within allowed ranges
            sentiment_score = max(1, min(5, int(result.get("sentiment_score", 3))))
            confidence = max(0, min(1, float(result.get("confidence", 0.5))))
            sentiment_label = result.get("sentiment_label", "neutral")
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'confidence': confidence
            }
            
        except Exception:
            # If OpenAI fails or is unavailable, return a neutral default
            pass
    
    # Default neutral sentiment if all methods fail
    return {
        'sentiment_score': 3,
        'sentiment_label': 'neutral',
        'confidence': 0.1  # Low confidence since this is a default
    }
