import streamlit as st

def initialize_achievements():
    """Initialize achievements in session state."""
    if 'achievements' not in st.session_state:
        st.session_state.achievements = set()

def award_points(activity_type: str, emissions_saved: float, bonus_points: float = 0, transport_type: str = ""):
    """Award points based on eco-friendly activities."""
    if 'points' not in st.session_state:
        st.session_state.points = 0

    initialize_achievements()

    # Add bonus points directly
    points = int(bonus_points * 100)  # Convert to whole numbers for easier tracking
    st.session_state.points += points

    # Add points based on emissions saved (if any)
    if emissions_saved > 0:
        emission_points = int(emissions_saved * 10)
        st.session_state.points += emission_points
        points += emission_points

    # Only check achievements if not using a car
    if transport_type != 'car':
        check_achievements()

    return points

def check_achievements():
    """Check and award achievements based on user activities."""
    points = st.session_state.points

    achievement_thresholds = {
        'Eco Warrior': 1000,
        'Carbon Crusher': 500,
        'Green Starter': 100,
        'Plant-Based Pioneer': 200, # Added achievement
        'Energy Saver': 300 # Added achievement

    }

    # Check point-based achievements
    for achievement, threshold in achievement_thresholds.items():
        if points >= threshold:
            add_achievement(achievement)

def get_achievements():
    """Get list of earned achievements."""
    initialize_achievements()
    return list(st.session_state.achievements)

def add_achievement(achievement_name: str):
    """Add a new achievement."""
    initialize_achievements()
    st.session_state.achievements.add(achievement_name)
    st.success(f"New Achievement Unlocked: {achievement_name}!")