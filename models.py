from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

# Create engine with proper connection parameters
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    display_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    profile_picture = Column(String, nullable=True)  # Store as base64
    points = Column(Integer, default=0)
    activities = relationship("Activity", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    bus_rides = relationship("BusRide", back_populates="user")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String)
    details = Column(String)
    emissions = Column(Float)
    date = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="activities")

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_name = Column(String)
    date_earned = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="achievements")

class BusRide(Base):
    __tablename__ = "bus_rides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    route_name = Column(String)
    distance = Column(Float)  # in miles
    points_earned = Column(Integer)
    date = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="bus_rides")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine)