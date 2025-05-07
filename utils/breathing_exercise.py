import streamlit as st
import time

def breathing_exercise():
    """
    Display and guide the user through a 4-4-4 breathing exercise.
    """
    st.title("🧘 Breathing Exercise")
    
    st.markdown("""
    ## 4-4-4 Breathing Technique
    
    This simple breathing exercise can help reduce stress and anxiety.
    
    - **Breathe in** for 4 seconds
    - **Hold** for 4 seconds
    - **Breathe out** for 4 seconds
    
    Ready to begin? Select how many rounds you'd like to do and click 'Start'.
    """)
    
    # Let user select number of rounds
    rounds = st.slider("Number of rounds", min_value=1, max_value=10, value=3)
    
    # Container for the exercise visualization
    exercise_container = st.empty()
    
    # Button to start exercise
    if st.button("Start Breathing Exercise"):
        with st.spinner("Preparing exercise..."):
            # Countdown to start
            for i in range(3, 0, -1):
                exercise_container.markdown(f"""
                <div style="text-align: center; margin-top: 50px;">
                    <h1>Starting in {i}...</h1>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
            
            # Run the breathing exercise for the selected number of rounds
            for round in range(1, rounds + 1):
                # Breathe in
                for i in range(4, 0, -1):
                    progress = (5 - i) / 4
                    size = 100 + (100 * progress)  # Circle grows from 100px to 200px
                    exercise_container.markdown(f"""
                    <div style="text-align: center; margin-top: 50px;">
                        <h2>Round {round}/{rounds}</h2>
                        <h1>Breathe In</h1>
                        <h2>{i}</h2>
                        <div style="background-color: rgba(142, 202, 230, {progress}); 
                                    border-radius: 50%; 
                                    width: {size}px; 
                                    height: {size}px; 
                                    margin: 30px auto;"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                
                # Hold breath
                for i in range(4, 0, -1):
                    exercise_container.markdown(f"""
                    <div style="text-align: center; margin-top: 50px;">
                        <h2>Round {round}/{rounds}</h2>
                        <h1>Hold</h1>
                        <h2>{i}</h2>
                        <div style="background-color: rgba(142, 202, 230, 1); 
                                    border-radius: 50%; 
                                    width: 200px; 
                                    height: 200px; 
                                    margin: 30px auto;"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                
                # Breathe out
                for i in range(4, 0, -1):
                    progress = i / 4
                    size = 100 + (100 * progress)  # Circle shrinks from 200px to 100px
                    exercise_container.markdown(f"""
                    <div style="text-align: center; margin-top: 50px;">
                        <h2>Round {round}/{rounds}</h2>
                        <h1>Breathe Out</h1>
                        <h2>{i}</h2>
                        <div style="background-color: rgba(142, 202, 230, {progress}); 
                                    border-radius: 50%; 
                                    width: {size}px; 
                                    height: {size}px; 
                                    margin: 30px auto;"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
            
            # Exercise complete
            exercise_container.markdown(f"""
            <div style="text-align: center; margin-top: 50px;">
                <h1>Exercise Complete</h1>
                <p style="font-size: 18px;">How do you feel?</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Provide options for how they feel after the exercise
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("I feel more relaxed"):
                    st.success("Great! Breathing exercises can be a powerful tool for relaxation.")
            with col2:
                if st.button("I feel the same"):
                    st.info("It's ok! Regular practice may help you feel the benefits over time.")
            with col3:
                if st.button("I want to try again"):
                    st.rerun()
    
    # Additional information about breathing exercises
    with st.expander("About Breathing Exercises"):
        st.markdown("""
        ### Benefits of Deep Breathing
        
        Deep breathing exercises like the 4-4-4 technique can help:
        
        - Reduce stress and anxiety
        - Lower blood pressure
        - Improve focus and concentration
        - Promote relaxation and better sleep
        - Reduce physical tension
        
        ### When to Use This Technique
        
        You can use this breathing exercise:
        
        - When feeling stressed or anxious
        - Before important events or meetings
        - To help fall asleep
        - During moments of frustration
        - As a daily mindfulness practice
        
        Regular practice can lead to better results over time.
        """)
