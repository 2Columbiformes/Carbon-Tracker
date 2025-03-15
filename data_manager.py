import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from sqlalchemy.orm import Session
from models import User, Activity, UserAchievement, get_db, BusRide # Assuming BusRide model exists
import os

def get_or_create_user(db: Session, username: str):
    """Get existing user or create new one."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def initialize_session_state():
    """Initialize session state variables."""
    if 'username' not in st.session_state:
        st.session_state.username = "default_user"
    if 'user_data' not in st.session_state:
        st.session_state.user_data = pd.DataFrame(columns=['date', 'activity_type', 'details', 'emissions'])

    # Get user from database
    db = next(get_db())
    user = get_or_create_user(db, st.session_state.username)
    st.session_state.user_id = user.id
    st.session_state.points = user.points

    # Update user_data from database
    activities = db.query(Activity).filter(Activity.user_id == user.id).all()
    if activities:
        data = []
        for activity in activities:
            data.append({
                'date': activity.date,
                'activity_type': activity.activity_type,
                'details': activity.details,
                'emissions': activity.emissions
            })
        st.session_state.user_data = pd.DataFrame(data)

def add_activity(activity_type: str, details: dict, emissions: float):
    """Add a new activity to the database and session state."""
    # Add to database
    db = next(get_db())
    activity = Activity(
        user_id=st.session_state.user_id,
        activity_type=activity_type,
        details=str(details),
        emissions=emissions
    )
    db.add(activity)
    db.commit()

    # Update session state data
    new_activity = pd.DataFrame([{
        'date': datetime.now(),
        'activity_type': activity_type,
        'details': str(details),
        'emissions': emissions
    }])
    st.session_state.user_data = pd.concat([st.session_state.user_data, new_activity], ignore_index=True)

def get_emissions_summary():
    """Get summary statistics of emissions from database."""
    db = next(get_db())
    now = datetime.now()

    activities = db.query(Activity).filter(
        Activity.user_id == st.session_state.user_id
    ).all()

    daily = sum(a.emissions for a in activities if now - a.date <= timedelta(days=1))
    weekly = sum(a.emissions for a in activities if now - a.date <= timedelta(days=7))
    monthly = sum(a.emissions for a in activities if now - a.date <= timedelta(days=30))

    return {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly
    }

def get_leaderboard_data():
    """Get leaderboard data from database."""
    db = next(get_db())
    users = db.query(User).order_by(User.points.desc()).limit(10).all()
    return [{'name': user.username, 'points': user.points} for user in users]

def update_user_points(points: int):
    """Update user points in database and session state."""
    db = next(get_db())
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    user.points += points
    db.commit()
    st.session_state.points = user.points

def add_achievement(achievement_name: str):
    """Add new achievement for user."""
    db = next(get_db())
    # Check if achievement already exists
    existing = db.query(UserAchievement).filter(
        UserAchievement.user_id == st.session_state.user_id,
        UserAchievement.achievement_name == achievement_name
    ).first()

    if not existing:
        achievement = UserAchievement(
            user_id=st.session_state.user_id,
            achievement_name=achievement_name
        )
        db.add(achievement)
        db.commit()

def get_user_achievements():
    """Get user's achievements from database."""
    db = next(get_db())
    achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == st.session_state.user_id
    ).all()
    return [achievement.achievement_name for achievement in achievements]

def update_user_profile(display_name: str = None, description: str = None, profile_picture: str = None):
    """Update user profile information."""
    db = next(get_db())
    user = db.query(User).filter(User.id == st.session_state.user_id).first()

    if display_name:
        user.display_name = display_name
    if description:
        user.description = description
    if profile_picture:
        user.profile_picture = profile_picture

    db.commit()
    db.refresh(user)
    return user

def get_user_profile():
    """Get user profile information."""
    db = next(get_db())
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    return {
        'display_name': user.display_name or user.username,
        'description': user.description or "No description provided",
        'profile_picture': user.profile_picture,
        'points': user.points
    }

def add_bus_ride(route_name: str, distance: float, points_earned: int):
    """Add a bus ride record and award points."""
    db = next(get_db())

    # Create bus ride record
    bus_ride = BusRide(
        user_id=st.session_state.user_id,
        route_name=route_name,
        distance=distance,
        points_earned=points_earned
    )
    db.add(bus_ride)

    # Update user points
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    user.points += points_earned
    st.session_state.points = user.points

    db.commit()
    return points_earned

def get_user_bus_rides():
    """Get user's bus ride history."""
    db = next(get_db())
    rides = db.query(BusRide).filter(
        BusRide.user_id == st.session_state.user_id
    ).order_by(BusRide.date.desc()).all()
    return rides