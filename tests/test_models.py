import pytest
from datetime import datetime, timedelta
from app import db
from app.models import User, ActivityType, Goal, ActivitySession, Achievement

def test_user_creation(app):
    """Test user creation and password hashing."""
    user = User(email='test@example.com')
    user.set_password('password123')
    
    assert user.email == 'test@example.com'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')

def test_activity_type_creation(app):
    """Test activity type creation."""
    activity_type = ActivityType(
        name='Running',
        calories_per_hour=600
    )
    
    assert activity_type.name == 'Running'
    assert activity_type.calories_per_hour == 600

def test_goal_creation(app, auth_client):
    """Test goal creation."""
    goal = Goal(
        user_id=1,  # Using the authenticated user's ID
        goal_type_id=1,
        target_value=10.0,
        fitness_level='beginner',
        available_time_per_week=5,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        is_completed=False
    )
    
    assert goal.user_id == 1
    assert goal.target_value == 10.0
    assert goal.fitness_level == 'beginner'
    assert not goal.is_completed

def test_activity_session_creation(app, auth_client):
    """Test activity session creation."""
    session = ActivitySession(
        user_id=1,
        activity_type_id=1,
        start_time=datetime.utcnow(),
        duration=30,
        calories_burned=300,
        is_completed=True
    )
    
    assert session.user_id == 1
    assert session.duration == 30
    assert session.calories_burned == 300
    assert session.is_completed

def test_achievement_creation(app):
    """Test achievement creation."""
    achievement = Achievement(
        title='First Activity',
        description='Complete your first activity',
        icon='fa-star'
    )
    
    assert achievement.title == 'First Activity'
    assert achievement.description == 'Complete your first activity'
    assert achievement.icon == 'fa-star'

def test_user_relationships(app, auth_client):
    """Test user relationships with other models."""
    # Create a user
    user = User.query.filter_by(email='test@example.com').first()
    
    # Create an activity type
    activity_type = ActivityType(name='Running', calories_per_hour=600)
    db.session.add(activity_type)
    
    # Create a goal
    goal = Goal(
        user_id=user.id,
        goal_type_id=1,
        target_value=10.0,
        fitness_level='beginner',
        available_time_per_week=5,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(goal)
    
    # Create an activity session
    session = ActivitySession(
        user_id=user.id,
        activity_type_id=activity_type.id,
        goal_id=goal.id,
        start_time=datetime.utcnow(),
        duration=30
    )
    db.session.add(session)
    
    db.session.commit()
    
    # Test relationships
    assert user.goals.count() == 1
    assert user.activity_sessions.count() == 1
    assert goal.user == user
    assert session.user == user
    assert session.activity_type == activity_type
    assert session.goal == goal 