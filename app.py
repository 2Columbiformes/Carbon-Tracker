import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64

from carbon_calculator import (
    calculate_transport_emissions,
    calculate_food_emissions,
    calculate_energy_emissions
)
from data_manager import (
    initialize_session_state,
    add_activity,
    get_emissions_summary,
    get_leaderboard_data,
    update_user_points,
    get_user_achievements,
    add_achievement,
    get_user_profile,
    update_user_profile,
    get_user_bus_rides,
    add_bus_ride
)
from gamification import award_points
from hawaii_data import get_sustainability_tips, get_tourist_recommendations
from energy_data import get_real_time_energy_data, get_local_activities
from map_data import create_oahu_map, get_store_locations, get_bus_routes
import streamlit.components.v1 as components

def set_page_style(page_name):
    """Set page-specific styling."""
    page_colors = {
        "Track Activities": {"bg": "#0a192f", "text": "#79ff83"},
        "Dashboard": {"bg": "#1a1a2e", "text": "#e94560"},
        "Energy Insights": {"bg": "#16213e", "text": "#79fffa"},
        "Local Activities": {"bg": "#1b2430", "text": "#00ff95"},
        "Tips & Recommendations": {"bg": "#2c3333", "text": "#00ffab"},
        "Achievements": {"bg": "#1e293b", "text": "#ffd700"},
        "Profile": {"bg": "#282c34", "text": "#8be9fd"}
    }

    colors = page_colors.get(page_name, {"bg": "#0d1117", "text": "#c9d1d9"})

    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {colors['bg']};
            color: {colors['text']};
        }}
        .achievement-card {{
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid {colors['text']};
        }}
        </style>
    """, unsafe_allow_html=True)

def show_profile():
    st.header("👤 User Profile")

    profile = get_user_profile()

    col1, col2 = st.columns([1, 2])

    with col1:
        if profile['profile_picture']:
            st.image(profile['profile_picture'], caption="Profile Picture")
        uploaded_file = st.file_uploader("Upload Profile Picture", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            # Convert the uploaded file to base64
            bytes_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode()
            update_user_profile(profile_picture=f"data:image/jpeg;base64,{base64_image}")
            st.success("Profile picture updated!")
            st.rerun()

    with col2:
        display_name = st.text_input("Display Name", value=profile['display_name'])
        description = st.text_area("About Me", value=profile['description'])

        if st.button("Update Profile"):
            update_user_profile(display_name=display_name, description=description)
            st.success("Profile updated successfully!")

    # Show bus ride history
    st.subheader("🚌 Bus Ride History")
    rides = get_user_bus_rides()

    if rides:
        ride_data = []
        for ride in rides:
            ride_data.append({
                'Date': ride.date.strftime('%Y-%m-%d %H:%M'),
                'Route': ride.route_name,
                'Distance (miles)': ride.distance,
                'Points Earned': ride.points_earned
            })

        df = pd.DataFrame(ride_data)
        st.dataframe(df)
    else:
        st.info("No bus rides recorded yet. Try taking TheBus to earn points!")

def show_achievements():
    st.header("🏆 Your Achievements")

    achievements = get_user_achievements()
    points = st.session_state.points

    # Display total points with custom styling
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <h2>Total Points: {points}</h2>
        </div>
    """, unsafe_allow_html=True)

    # Define all possible achievements
    all_achievements = {
        'Eco Warrior': {'points': 1000, 'icon': '🌍', 'description': 'Earned 1000+ points through eco-friendly choices'},
        'Carbon Crusher': {'points': 500, 'icon': '💪', 'description': 'Reached 500 points in carbon reduction'},
        'Green Starter': {'points': 100, 'icon': '🌱', 'description': 'Started your journey with 100 points'},
        'Green Commuter': {'icon': '🚲', 'description': 'Chose eco-friendly transportation'},
        'Plant-Based Pioneer': {'icon': '🥗', 'description': 'Made sustainable food choices'},
        'Energy Saver': {'icon': '⚡', 'description': 'Demonstrated energy conservation'}
    }

    # Create two columns for achievements display
    col1, col2 = st.columns(2)

    # Display achievements in a grid
    for i, (name, details) in enumerate(all_achievements.items()):
        with col1 if i % 2 == 0 else col2:
            is_earned = name in achievements
            if 'points' in details:
                is_earned = points >= details['points']
            status = "🔓 Unlocked" if is_earned else "🔒 Locked"
            if 'points' in details and not is_earned:
                status += f" (Requires {details['points']} points)"

            st.markdown(f"""
                <div class='achievement-card' style='opacity: {"1" if is_earned else "0.6"}'>
                    <h3>{details['icon']} {name}</h3>
                    <p>{details['description']}</p>
                    <p><small>{status}</small></p>
                </div>
            """, unsafe_allow_html=True)

def show_energy_insights():
    st.header("Real-Time Energy Insights")

    # Get real-time energy data
    energy_data = get_real_time_energy_data()

    # Create columns for metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Demand", f"{energy_data['total_demand']} MW")
    with col2:
        st.metric("Solar Contribution", f"{energy_data['solar_contribution']} MW")
    with col3:
        st.metric("Wind Contribution", f"{energy_data['wind_contribution']} MW")

    # Display renewable percentage
    st.progress(energy_data['renewable_percentage'] / 100)
    st.text(f"Current Renewable Energy: {energy_data['renewable_percentage']}%")

    # Add a chart showing energy distribution
    energy_dist = pd.DataFrame({
        'Source': ['Solar', 'Wind', 'Other'],
        'Contribution': [
            energy_data['solar_contribution'],
            energy_data['wind_contribution'],
            energy_data['total_demand'] - energy_data['solar_contribution'] - energy_data['wind_contribution']
        ]
    })

    fig = px.pie(energy_dist, values='Contribution', names='Source', title='Current Energy Distribution')
    st.plotly_chart(fig)

def show_local_activities():
    st.header("Local Sustainability Activities")

    activities = get_local_activities()

    for activity in activities:
        with st.expander(f"{activity['type']} - {activity['date']}"):
            st.write(f"📍 Location: {activity['location']}")
            st.write(f"🌱 Impact: {activity['impact']}")
            st.write(f"🏆 Points: {activity['points']}")

            if st.button(f"Join {activity['type']}", key=f"join_{activity['type']}"):
                update_user_points(activity['points'])
                st.success(f"You've signed up for {activity['type']} and earned {activity['points']} points!")

def show_activity_tracking():
    st.header("Track Your Activities")

    activity_type = st.selectbox(
        "Select activity type",
        ["Transport", "Food", "Energy"]
    )

    if activity_type == "Transport":
        transport_type = st.selectbox(
            "Transportation method",
            ["car", "bus", "walk", "bike", "electric_vehicle"]
        )
        distance = st.number_input("Distance (miles)", min_value=0.0, step=0.1)

        if st.button("Log Transport Activity"):
            emissions, bonus_points = calculate_transport_emissions(transport_type, distance)
            details = {"type": transport_type, "distance": distance}
            add_activity("transport", details, emissions)

            # Award points based on transportation choice
            points = award_points("transport", 0, bonus_points, transport_type=transport_type)

            # Update the user points immediately after awarding
            update_user_points(points)

            if transport_type == 'car':
                st.info("Activity logged. Consider eco-friendly options like walking, biking, or public transit next time!")
            elif points > 0:
                st.success(f"Great choice! You earned {points} points for choosing eco-friendly transportation!")

                # Add achievement for eco-friendly transport
                if transport_type in ['walk', 'bike', 'bus']:
                    add_achievement("Green Commuter")

    elif activity_type == "Food":
        food_type = st.selectbox(
            "Food type",
            ["meat", "fish", "vegetarian", "vegan"]
        )
        portions = st.number_input("Number of portions", min_value=1, step=1)

        if st.button("Log Food Activity"):
            emissions = calculate_food_emissions(food_type, portions)
            details = {"type": food_type, "portions": portions}
            add_activity("food", details, emissions)

            # Award points for eco-friendly choices
            if food_type in ["vegetarian", "vegan"]:
                meat_emissions = calculate_food_emissions("meat", portions)
                points = award_points("food", meat_emissions - emissions)
                update_user_points(points)
                st.success(f"Logged successfully! Earned {points} points!")

                # Add achievement for eco-friendly food choices
                add_achievement("Plant-Based Pioneer")
            else:
                st.success("Activity logged successfully!")

    elif activity_type == "Energy":
        kwh = st.number_input("Energy usage (kWh)", min_value=0.0, step=0.1)

        if st.button("Log Energy Activity"):
            emissions = calculate_energy_emissions(kwh)
            details = {"kwh": kwh}
            add_activity("energy", details, emissions)

            # Award points for low energy usage
            if kwh < 10:  # Example threshold for low energy usage
                points = award_points("energy", emissions)
                update_user_points(points)
                st.success(f"Great job on energy conservation! Earned {points} points!")
                add_achievement("Energy Saver")
            else:
                st.success("Activity logged successfully!")

def show_dashboard():
    st.header("Your Carbon Footprint Dashboard")

    # Show emissions summary
    summary = get_emissions_summary()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Daily Emissions", f"{summary['daily']:.2f} kg CO2")
    with col2:
        st.metric("Weekly Emissions", f"{summary['weekly']:.2f} kg CO2")
    with col3:
        st.metric("Monthly Emissions", f"{summary['monthly']:.2f} kg CO2")

    # Show emissions trend
    if hasattr(st.session_state, 'user_data') and not st.session_state.user_data.empty:
        fig = px.line(
            st.session_state.user_data,
            x='date',
            y='emissions',
            title='Your Emissions Over Time'
        )
        st.plotly_chart(fig)
    else:
        st.info("Start logging activities to see your emissions trend!")

    # Show leaderboard
    st.subheader("Leaderboard")
    leaderboard = get_leaderboard_data()

    if leaderboard:
        for i, entry in enumerate(leaderboard, 1):
            st.text(f"{i}. {entry['name']}: {entry['points']} points")
    else:
        st.info("Be the first one on the leaderboard!")

def show_tips():
    st.header("Hawaii Sustainability Tips")

    tips = get_sustainability_tips()
    recommendations = get_tourist_recommendations()

    # Display tips by category
    for category, category_tips in tips.items():
        st.subheader(f"{category.title()} Tips")
        for tip in category_tips:
            st.write(f"• {tip}")

    st.header("Eco-Tourist Recommendations")
    for section in recommendations:
        st.subheader(section['title'])
        for item in section['items']:
            st.write(f"• {item}")

def show_rewards_map():
    st.header("🗺️ Oahu Activities and Rewards Map")

    # Display current points and available rewards
    st.subheader("Your Rewards Status")
    points = st.session_state.points
    st.info(f"Current Points: {points}")

    # Add Bus Route Simulation
    st.subheader("🚌 Simulate Bus Ride")
    routes = get_bus_routes()
    selected_route = st.selectbox(
        "Select a bus route",
        options=[route['name'] for route in routes]
    )

    selected_route_data = next(route for route in routes if route['name'] == selected_route)

    if st.button("Record Bus Ride"):
        points_earned = add_bus_ride(
            selected_route,
            selected_route_data['distance'],
            selected_route_data['points_per_ride']
        )
        st.success(f"Bus ride recorded! You earned {points_earned} points!")
        st.rerun()

    # Show available store rewards
    st.subheader("Available Store Rewards")
    stores = get_store_locations()

    # Create three columns for store rewards
    cols = st.columns(3)
    for idx, store in enumerate(stores):
        with cols[idx]:
            status = "🔓 Unlocked" if points >= store['points_required'] else "🔒 Locked"
            st.markdown(f"""
                <div style='padding: 10px; background-color: rgba(255, 255, 255, 0.1); border-radius: 5px;'>
                    <h4>{store['name']}</h4>
                    <p>{store['description']}</p>
                    <p>Required: {store['points_required']} points</p>
                    <p>Reward: {store['discount']}</p>
                    <p><strong>{status}</strong></p>
                </div>
            """, unsafe_allow_html=True)

    # Create and display the map
    st.subheader("Interactive Map")
    m = create_oahu_map(points)

    # Get the HTML representation of the map
    map_html = m._repr_html_()

    # Display the map using components
    components.html(map_html, height=600)

    st.markdown("""
        ### Map Legend
        - 🔵 Blue Lines: Bus Routes
        - 🟢 Green Markers: Available activities
        - 🔴 Red Markers: Locked store rewards
        - 🟢 Green Store Markers: Unlocked rewards

        Click on any marker to see more details!
    """)


def main():
    st.set_page_config(page_title="Hawaii Carbon Footprint Tracker", layout="wide")

    # Initialize session state
    initialize_session_state()

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ["Profile", "Track Activities", "Dashboard", "Energy Insights", 
         "Local Activities", "Tips & Recommendations", "Achievements", "Rewards Map"]
    )

    # Set page-specific styling
    set_page_style(page)

    # Display username and points in sidebar
    st.sidebar.markdown(f"""
        <div style='padding: 10px; background-color: rgba(255, 255, 255, 0.1); border-radius: 5px;'>
            <h3>User Profile</h3>
            <p>User: {st.session_state.username}</p>
            <p>Points: {st.session_state.points}</p>
        </div>
    """, unsafe_allow_html=True)

    if page == "Profile":
        show_profile()
    elif page == "Track Activities":
        show_activity_tracking()
    elif page == "Dashboard":
        show_dashboard()
    elif page == "Energy Insights":
        show_energy_insights()
    elif page == "Local Activities":
        show_local_activities()
    elif page == "Tips & Recommendations":
        show_tips()
    elif page == "Achievements":
        show_achievements()
    else:
        show_rewards_map()
    st.image("generated-icon.png", caption="Hawaii Carbon Footprint Tracker", width=200)


if __name__ == "__main__":
    main()