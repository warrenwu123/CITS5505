import pytest
from datetime import datetime, timedelta
from app import db
from flask import url_for
from app.models import User, ActivityType, Goal, ActivitySession, Achievement

def test_index_page(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 302  # Redirects to login

def test_index_page_authenticated(auth_client):
    """Test the index page when authenticated."""
    response = auth_client.get('/')
    assert response.status_code == 200

def test_profile_page(auth_client):
    """Test the profile page."""
    response = auth_client.get('/profile')
    assert response.status_code == 200

def test_goals_page(auth_client):
    """Test the goals page."""
    response = auth_client.get('/goals')
    assert response.status_code == 200

def test_achievements_page(auth_client):
    """Test the achievements page."""
    response = auth_client.get('/achievements')
    assert response.status_code == 200

def test_create_goal(auth_client):
    """Test creating a new goal."""
    data = {
        'goal_type': 'weightloss',
        'target_value': 10.0,
        'fitness_level': 'beginner',
        'available_time_per_week': 5,
        'end_date': '2024-12-31'
    }
    
    response = auth_client.post('/api/create-goal', json=data)
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Verify goal was created
    goal = Goal.query.filter_by(user_id=1).first()
    assert goal is not None
    assert goal.target_value == 10.0
    assert goal.fitness_level == 'beginner'

def test_log_activity(auth_client):
    """Test logging a new activity."""
    data = {
        'activity_type_id': 1,
        'duration': 30,
        'calories_burned': 300,
        'notes': 'Test activity'
    }
    
    response = auth_client.post('/api/log-activity', json=data)
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Verify activity was logged
    activity = ActivitySession.query.filter_by(user_id=1).first()
    assert activity is not None
    assert activity.duration == 30
    assert activity.calories_burned == 300

def test_complete_session(auth_client):
    """Test completing an activity session."""
    # First create a session
    session = ActivitySession(
        user_id=1,
        activity_type_id=1,
        start_time=datetime.utcnow(),
        duration=30,
        is_completed=False
    )
    db.session.add(session)
    db.session.commit()
    
    # Then complete it
    response = auth_client.post(f'/api/sessions/{session.id}/complete', json={
        'remaining_seconds': 0
    })
    assert response.status_code == 200
    
    # Verify session was completed
    session = ActivitySession.query.get(session.id)
    assert session.is_completed == True

def test_leaderboard_page(auth_client):
    """Test the leaderboard page."""
    response = auth_client.get('/leaderboard')
    assert response.status_code == 200

def test_social_page(auth_client):
    """Test the social page."""
    response = auth_client.get('/social')
    assert response.status_code == 200

def test_follow_user(auth_client):
    """Test following another user."""
    # Create another user
    other_user = User(email='other@example.com')
    other_user.set_password('password123')
    db.session.add(other_user)
    db.session.commit()
    
    # Try to follow
    response = auth_client.post(f'/api/follow/{other_user.id}')
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Verify follow relationship
    user = User.query.get(1)
    assert user.is_following(other_user)

def test_unfollow_user(auth_client):
    """Test unfollowing a user."""
    # Create another user
    other_user = User(email='other@example.com')
    other_user.set_password('password123')
    db.session.add(other_user)
    db.session.commit()
    
    # First follow
    user = User.query.get(1)
    user.follow(other_user)
    db.session.commit()
    
    # Then unfollow
    response = auth_client.post(f'/api/unfollow/{other_user.id}')
    assert response.status_code == 200
    assert response.json['success'] == True
    
    # Verify unfollow
    assert not user.is_following(other_user) 