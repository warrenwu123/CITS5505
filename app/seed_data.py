from app import app, db
from app.models import ActivityType, FitnessLevelConfig, GoalType, User, MFAToken, PasswordResetToken, EmailVerificationToken, ActivitySession, Achievement, UserAchievement, Goal, Follow

with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    from .models import User, MFAToken, PasswordResetToken, EmailVerificationToken,ActivityType, ActivitySession, Achievement, UserAchievement, Goal, Follow, FitnessLevelConfig, GoalType
    
    db.create_all()

    default_activities = [
        "Running", "Walking", "Cycling", "Swimming",
        "Barbell Squat", "Bench Press", "Deadlift",
        "Chin-up", "Military Press", "Push-up",
        "Flexibility Training"
    ]
    for name in default_activities:
        exists = ActivityType.query.filter_by(name=name).first()
        if not exists:
            db.session.add(ActivityType(name=name))
    db.session.commit()

    running = ActivityType.query.filter_by(name='Running').first()
    cycling = ActivityType.query.filter_by(name='Cycling').first()
    walking = ActivityType.query.filter_by(name='Walking').first()
    swimming = ActivityType.query.filter_by(name='Swimming').first()
    squat = ActivityType.query.filter_by(name='Barbell Squat').first()
    bench = ActivityType.query.filter_by(name='Bench Press').first()
    deadlift = ActivityType.query.filter_by(name='Deadlift').first()
    chinup = ActivityType.query.filter_by(name='Chin-up').first()
    military = ActivityType.query.filter_by(name='Military Press').first()
    pushup = ActivityType.query.filter_by(name='Push-up').first()

# Create fitness level configurations
    configs = [

    
    FitnessLevelConfig(activity_type_id=running.id, fitness_level='beginner', duration_minutes=15),
    FitnessLevelConfig(activity_type_id=running.id, fitness_level='novice', duration_minutes=20),
    FitnessLevelConfig(activity_type_id=running.id, fitness_level='intermediate', duration_minutes=30),
    FitnessLevelConfig(activity_type_id=running.id, fitness_level='advanced', duration_minutes=40),
    FitnessLevelConfig(activity_type_id=running.id, fitness_level='elite', duration_minutes=60),

    FitnessLevelConfig(activity_type_id=cycling.id, fitness_level='beginner', duration_minutes=20),
    FitnessLevelConfig(activity_type_id=cycling.id, fitness_level='novice', duration_minutes=30),
    FitnessLevelConfig(activity_type_id=cycling.id, fitness_level='intermediate', duration_minutes=45),
    FitnessLevelConfig(activity_type_id=cycling.id, fitness_level='advanced', duration_minutes=60),
    FitnessLevelConfig(activity_type_id=cycling.id, fitness_level='elite', duration_minutes=90),

    FitnessLevelConfig(activity_type_id=walking.id, fitness_level='beginner', duration_minutes=30),
    FitnessLevelConfig(activity_type_id=walking.id, fitness_level='novice', duration_minutes=40),
    FitnessLevelConfig(activity_type_id=walking.id, fitness_level='intermediate', duration_minutes=60),
    FitnessLevelConfig(activity_type_id=walking.id, fitness_level='advanced', duration_minutes=90),
    FitnessLevelConfig(activity_type_id=walking.id, fitness_level='elite', duration_minutes=120),

    FitnessLevelConfig(activity_type_id=swimming.id, fitness_level='beginner', duration_minutes=15),
    FitnessLevelConfig(activity_type_id=swimming.id, fitness_level='novice', duration_minutes=20),
    FitnessLevelConfig(activity_type_id=swimming.id, fitness_level='intermediate', duration_minutes=30),
    FitnessLevelConfig(activity_type_id=swimming.id, fitness_level='advanced', duration_minutes=40),
    FitnessLevelConfig(activity_type_id=swimming.id, fitness_level='elite', duration_minutes=60),

    
    FitnessLevelConfig(activity_type_id=squat.id, fitness_level='beginner', weight_ratio=0.5, reps=8, sets=3),
    FitnessLevelConfig(activity_type_id=squat.id, fitness_level='novice', weight_ratio=0.7, reps=8, sets=4),
    FitnessLevelConfig(activity_type_id=squat.id, fitness_level='intermediate', weight_ratio=1.0, reps=6, sets=4),
    FitnessLevelConfig(activity_type_id=squat.id, fitness_level='advanced', weight_ratio=1.5, reps=5, sets=5),
    FitnessLevelConfig(activity_type_id=squat.id, fitness_level='elite', weight_ratio=2.0, reps=3, sets=5),

    FitnessLevelConfig(activity_type_id=bench.id, fitness_level='beginner', weight_ratio=0.4, reps=8, sets=3),
    FitnessLevelConfig(activity_type_id=bench.id, fitness_level='novice', weight_ratio=0.6, reps=8, sets=4),
    FitnessLevelConfig(activity_type_id=bench.id, fitness_level='intermediate', weight_ratio=0.8, reps=6, sets=4),
    FitnessLevelConfig(activity_type_id=bench.id, fitness_level='advanced', weight_ratio=1.2, reps=5, sets=5),
    FitnessLevelConfig(activity_type_id=bench.id, fitness_level='elite', weight_ratio=1.5, reps=3, sets=5),

    FitnessLevelConfig(activity_type_id=deadlift.id, fitness_level='beginner', weight_ratio=0.6, reps=8, sets=3),
    FitnessLevelConfig(activity_type_id=deadlift.id, fitness_level='novice', weight_ratio=0.8, reps=8, sets=4),
    FitnessLevelConfig(activity_type_id=deadlift.id, fitness_level='intermediate', weight_ratio=1.2, reps=6, sets=4),
    FitnessLevelConfig(activity_type_id=deadlift.id, fitness_level='advanced', weight_ratio=1.6, reps=5, sets=5),
    FitnessLevelConfig(activity_type_id=deadlift.id, fitness_level='elite', weight_ratio=2.0, reps=3, sets=5),

    FitnessLevelConfig(activity_type_id=chinup.id, fitness_level='beginner', reps=3, sets=3),
    FitnessLevelConfig(activity_type_id=chinup.id, fitness_level='novice', reps=5, sets=3),
    FitnessLevelConfig(activity_type_id=chinup.id, fitness_level='intermediate', reps=8, sets=4),
    FitnessLevelConfig(activity_type_id=chinup.id, fitness_level='advanced', reps=10, sets=5),
    FitnessLevelConfig(activity_type_id=chinup.id, fitness_level='elite', reps=15, sets=5),

    FitnessLevelConfig(activity_type_id=military.id, fitness_level='beginner', weight_ratio=0.3, reps=8, sets=3),
    FitnessLevelConfig(activity_type_id=military.id, fitness_level='novice', weight_ratio=0.5, reps=8, sets=4),
    FitnessLevelConfig(activity_type_id=military.id, fitness_level='intermediate', weight_ratio=0.7, reps=6, sets=4),
    FitnessLevelConfig(activity_type_id=military.id, fitness_level='advanced', weight_ratio=1.0, reps=5, sets=5),
    FitnessLevelConfig(activity_type_id=military.id, fitness_level='elite', weight_ratio=1.3, reps=3, sets=5),

    FitnessLevelConfig(activity_type_id=pushup.id, fitness_level='beginner', reps=10, sets=3),
    FitnessLevelConfig(activity_type_id=pushup.id, fitness_level='novice', reps=15, sets=3),
    FitnessLevelConfig(activity_type_id=pushup.id, fitness_level='intermediate', reps=20, sets=4),
    FitnessLevelConfig(activity_type_id=pushup.id, fitness_level='advanced', reps=30, sets=5),
    FitnessLevelConfig(activity_type_id=pushup.id, fitness_level='elite', reps=50, sets=5),
]

    db.session.add_all(configs)
    db.session.commit()

    from app.models import GoalType

    goal_types = [
        {"name": "weightloss", "description": "Lose body fat and reduce body weight"},
        {"name": "weightgain", "description": "Gain muscle mass or body weight"},
        {"name": "endurance", "description": "Improve cardiovascular endurance and stamina"},
        {"name": "strength", "description": "Increase muscular strength and power"}
    ]

    for gt in goal_types:
        exists = GoalType.query.filter_by(name=gt['name']).first()
        if not exists:
            db.session.add(GoalType(name=gt['name'], description=gt['description']))
