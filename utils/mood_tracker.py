import pandas as pd
import streamlit as st
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def save_mood(mood_score, mood_label, notes=""):
    """
    Save the user's mood to a CSV file.
    
    Args:
        mood_score: Numerical score (1-5)
        mood_label: Text label for the mood
        notes: Optional notes from the user
    """
    # Create a DataFrame for the new mood entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.now().strftime("%Y-%m-%d")
    new_entry = pd.DataFrame({
        'timestamp': [timestamp],
        'date': [date],
        'mood_score': [mood_score],
        'mood_label': [mood_label],
        'notes': [notes]
    })
    
    # Load existing data if file exists
    if os.path.exists("mood_data.csv"):
        try:
            existing_data = pd.read_csv("mood_data.csv")
            # Append new entry
            updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        except Exception:
            # If there's an error reading the file, start fresh
            updated_data = new_entry
    else:
        # Create new file if it doesn't exist
        updated_data = new_entry
    
    # Save the updated data
    updated_data.to_csv("mood_data.csv", index=False)

def get_mood_history():
    """
    Retrieve the user's mood history from the CSV file.
    
    Returns:
        DataFrame containing mood history or None if no data exists
    """
    if os.path.exists("mood_data.csv"):
        try:
            data = pd.read_csv("mood_data.csv")
            # Convert timestamp strings to datetime objects
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data['date'] = pd.to_datetime(data['date'])
            return data
        except Exception:
            return None
    return None

def display_mood_chart(mood_data):
    """
    Display a chart of the user's mood history.
    
    Args:
        mood_data: DataFrame containing mood data
    """
    # Create a 7-day rolling average
    mood_data = mood_data.sort_values('date')
    
    # Create daily average mood if multiple entries per day
    daily_mood = mood_data.groupby('date')['mood_score'].mean().reset_index()
    daily_mood['date'] = pd.to_datetime(daily_mood['date'])
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # Set a soothing color palette
    colors = ['#8ecae6', '#219ebc', '#023047', '#ffb703', '#fb8500']
    
    # Plot 1: Line chart of mood over time
    ax1.plot(daily_mood['date'], daily_mood['mood_score'], marker='o', linestyle='-', color=colors[1], linewidth=2)
    
    # Add a rolling average if there are enough data points
    if len(daily_mood) >= 3:
        rolling_avg = daily_mood['mood_score'].rolling(window=3, min_periods=1).mean()
        ax1.plot(daily_mood['date'], rolling_avg, linestyle='--', color=colors[2], linewidth=1.5, alpha=0.7, label='3-day average')
        ax1.legend()
    
    # Set y-axis limits with some padding
    ax1.set_ylim(0.5, 5.5)
    
    # Add mood labels to y-axis
    ax1.set_yticks([1, 2, 3, 4, 5])
    ax1.set_yticklabels(['Very Sad', 'Sad', 'Neutral', 'Happy', 'Very Happy'])
    
    # Format the chart
    ax1.set_title('Your Mood History', fontsize=16)
    ax1.set_xlabel('Date', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Add explanatory text
    if len(daily_mood) >= 7:
        # Calculate trend direction
        recent_avg = daily_mood['mood_score'].iloc[-3:].mean()
        earlier_avg = daily_mood['mood_score'].iloc[-7:-3].mean()
        trend_diff = recent_avg - earlier_avg
        
        if abs(trend_diff) < 0.5:
            trend_text = "Your mood has been relatively stable recently."
        elif trend_diff > 0:
            trend_text = "Your mood appears to be improving over the past week."
        else:
            trend_text = "Your mood has been trending lower recently."
            
        fig.text(0.5, 0.01, trend_text, ha='center', fontsize=12)
    
    # Plot 2: Distribution of moods
    mood_counts = mood_data['mood_score'].value_counts().sort_index()
    bars = ax2.bar(mood_counts.index, mood_counts.values, color=colors, alpha=0.7)
    
    # Add count labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{int(height)}', ha='center', va='bottom')
    
    # Set x-axis labels
    ax2.set_xticks([1, 2, 3, 4, 5])
    ax2.set_xticklabels(['Very Sad', 'Sad', 'Neutral', 'Happy', 'Very Happy'])
    ax2.set_title('Mood Distribution', fontsize=14)
    
    # Adjust layout and display the chart
    plt.tight_layout(pad=3.0)
    st.pyplot(fig)
    
    # Display a table of recent entries with dates and notes
    st.subheader("Recent Entries")
    recent_entries = mood_data.sort_values('timestamp', ascending=False).head(5)
    
    # Create a more readable table
    display_table = recent_entries[['date', 'mood_label', 'notes']].copy()
    display_table['date'] = recent_entries['date'].dt.strftime('%Y-%m-%d')
    display_table.columns = ['Date', 'Mood', 'Notes']
    
    st.table(display_table)
