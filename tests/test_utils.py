import pytest
from datetime import datetime, timedelta
from app import db
from app.models import User, ActivityType, Goal, ActivitySession, Achievement
from app.util.util import (
    generate_weightloss_plan,
    generate_strength_plan,
    generate_weightgain_plan,
    generate_endurance_plan
)

def test_generate_weightloss_plan(app):
    """Test weight loss plan generation."""
    # Create necessary activity types
    activity_types = [
        ActivityType(name='Running', calories_per_hour=600),
        ActivityType(name='Cycling', calories_per_hour=400),
        ActivityType(name='Swimming', calories_per_hour=500)
    ]
    db.session.add_all(activity_types)
    db.session.commit()
    
    # Create a test goal
    goal = Goal(
        user_id=1,
        goal_type_id=1,  # weightloss
        target_value=10.0,  # 10kg
        fitness_level='beginner',
        available_time_per_week=5,  # 5 hours
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    # Generate plan
    plan = generate_weightloss_plan(goal)
    
    # Verify plan structure
    assert 'plan' in plan
    assert len(plan['plan']) > 0
    
    # Verify plan contents
    for activity in plan['plan']:
        assert 'activity' in activity
        assert 'target_minutes_per_week' in activity
        assert 'expected_calories_burned_per_week' in activity

def test_generate_strength_plan(app):
    """Test strength training plan generation."""
    # Create necessary activity types
    activity_types = [
        ActivityType(name='Weightlifting', calories_per_hour=300),
        ActivityType(name='Push-ups', calories_per_hour=200),
        ActivityType(name='Pull-ups', calories_per_hour=200)
    ]
    db.session.add_all(activity_types)
    db.session.commit()
    
    # Create a test goal
    goal = Goal(
        user_id=1,
        goal_type_id=2,  # strength
        target_value=5.0,  # 5kg increase
        fitness_level='beginner',
        available_time_per_week=3,  # 3 hours
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    # Generate plan
    plan = generate_strength_plan(goal)
    
    # Verify plan structure
    assert len(plan) > 0
    
    # Verify plan contents
    for exercise in plan:
        assert 'activity' in exercise
        assert 'sets' in exercise
        assert 'reps' in exercise
        assert 'rounds_per_week' in exercise

def test_generate_weightgain_plan(app):
    """Test weight gain plan generation."""
    # Create necessary activity types
    activity_types = [
        ActivityType(name='Weightlifting', calories_per_hour=300),
        ActivityType(name='Squats', calories_per_hour=250),
        ActivityType(name='Deadlifts', calories_per_hour=300)
    ]
    db.session.add_all(activity_types)
    db.session.commit()
    
    # Create a test goal
    goal = Goal(
        user_id=1,
        goal_type_id=3,  # weightgain
        target_value=5.0,  # 5kg
        fitness_level='beginner',
        available_time_per_week=4,  # 4 hours
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    # Generate plan
    plan = generate_weightgain_plan(goal)
    
    # Verify plan structure
    assert 'strength_training' in plan
    assert len(plan['strength_training']) > 0
    
    # Verify plan contents
    for exercise in plan['strength_training']:
        assert 'activity' in exercise
        assert 'sets' in exercise
        assert 'reps' in exercise
        assert 'rounds_per_week' in exercise

def test_generate_endurance_plan(app):
    """Test endurance plan generation."""
    # Create necessary activity types
    activity_types = [
        ActivityType(name='Running', calories_per_hour=600),
        ActivityType(name='Cycling', calories_per_hour=400),
        ActivityType(name='Swimming', calories_per_hour=500)
    ]
    db.session.add_all(activity_types)
    db.session.commit()
    
    # Create a test goal
    goal = Goal(
        user_id=1,
        goal_type_id=4,  # endurance
        target_value=10.0,  # 10km
        fitness_level='beginner',
        available_time_per_week=5,  # 5 hours
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    # Generate plan
    plan = generate_endurance_plan(goal)
    
    # Verify plan structure
    assert 'plan' in plan
    assert len(plan['plan']) > 0
    
    # Verify plan contents
    for activity in plan['plan']:
        assert 'activity' in activity
        assert 'target_minutes_per_week' in activity
        assert 'expected_calories_burned_per_week' in activity 