import pytest
from app import create_app, db
from app.models.user import User
from app.models.activity import (
    ActivityType, Goal, ActivitySession, Achievement,
    GoalType, UserAchievement
)
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client):
    """A test client with an authenticated user."""
    # Create a test user
    user = User(email='Warren_Wu1@hotmail.com')
    user.set_password('QEWyop?=!,58458')
    db.session.add(user)
    db.session.commit()
    
    # Log in the user
    client.post('/auth/sign-in', data={
        'email': 'Warren_Wu1@hotmail.com',
        'password': 'QEWyop?=!,58458',
        'remember_me': False
    })
    
    return client

@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_goal_type(app):
    """Create a test goal type."""
    goal_type = GoalType(name='Weight Loss', description='Lose weight')
    db.session.add(goal_type)
    db.session.commit()
    return goal_type

@pytest.fixture
def test_goal(app, test_user, test_goal_type):
    """Create a test goal."""
    goal = Goal(
        user_id=test_user.id,
        goal_type_id=test_goal_type.id,
        target_value=10.0,
        fitness_level='beginner',
        available_time_per_week=5,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(goal)
    db.session.commit()
    return goal

@pytest.fixture
def test_activity_type(app):
    """Create a test activity type."""
    activity_type = ActivityType(name='Running', calories_per_hour=600)
    db.session.add(activity_type)
    db.session.commit()
    return activity_type

@pytest.fixture
def test_activity_session(app, test_user, test_activity_type, test_goal):
    """Create a test activity session."""
    session = ActivitySession(
        user_id=test_user.id,
        activity_type_id=test_activity_type.id,
        goal_id=test_goal.id,
        start_time=datetime.utcnow(),
        duration=30,
        calories_burned=300
    )
    db.session.add(session)
    db.session.commit()
    return session

@pytest.fixture
def test_achievement(app):
    """Create a test achievement."""
    achievement = Achievement(
        title='First Activity',
        description='Complete your first activity',
        icon='fa-star'
    )
    db.session.add(achievement)
    db.session.commit()
    return achievement

@pytest.fixture
def test_user_achievement(app, test_user, test_achievement):
    """Create a test user achievement."""
    user_achievement = UserAchievement(
        user_id=test_user.id,
        achievement_id=test_achievement.id,
        date_earned=datetime.utcnow()
    )
    db.session.add(user_achievement)
    db.session.commit()
    return user_achievement 