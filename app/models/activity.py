import datetime
from app import db
from sqlalchemy.sql import func

class ActivityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    calories_per_hour = db.Column(db.Float, nullable=True)
    
    # Relationships
    activity_sessions = db.relationship('ActivitySession', backref='activity_type', lazy=True)
    goals = db.relationship('Goal', backref='activity_type', lazy=True)
    fitness_level_configs = db.relationship('FitnessLevelConfig', backref='activity_type', lazy=True)
    goal_types = db.relationship('GoalType', secondary='activity_type_plan_type', lazy='subquery',
                                 backref=db.backref('activity_types', lazy=True))
    
    def __repr__(self):
        return f'<ActivityType {self.name}>'
    def to_dict(self):
        return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'icon': self.icon,
                'calories_per_hour': self.calories_per_hour
            }
        
activity_type_plan_type = db.Table(
    'activity_type_plan_type',
    db.Column('activity_type_id', db.Integer, db.ForeignKey('activity_type.id'), primary_key=True),
    db.Column('goal_type_id', db.Integer, db.ForeignKey('goal_type.id'), primary_key=True)
)


class GoalType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    goals = db.relationship('Goal', backref='goal_type', lazy=True)

    
    def __repr__(self):
        return f'<GoalType {self.name}>'
    def to_dict(self):
        return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
            }
    
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False,name='user_id')
    fitness_level = db.Column(
        db.Enum('beginner', 'novice', 'intermediate', 'advanced', 'elite', name='fitnesslevelenum'),
        nullable=False
    )
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False,name='activity_type_id')
    goal_type_id = db.Column(db.Integer, db.ForeignKey('goal_type.id'), nullable=False,name='goal_type_id') 
    target_value = db.Column(db.Float, nullable=False)
    available_time_per_week = db.Column(db.Float, nullable=False)  
    start_date = db.Column(db.DateTime, nullable=False, default=func.now())
    end_date = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<Goal {self.goal_type} {self.target_value}>'

    
class ActivitySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=True)
    goal_type_id = db.Column(db.Integer, db.ForeignKey('goal_type.id'), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, default=func.now())
    end_time = db.Column(db.DateTime, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Interval, nullable=True)
    calories_burned = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<ActivitySession {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type_id': self.activity_type_id,
            'goal_id': self.goal_id,
            'goal_type_id': self.goal_type_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'sets': self.sets,
            'reps': self.reps,
            'duration': str(self.duration) if self.duration else None,
            'calories_burned': self.calories_burned,
            'notes': self.notes,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    requirement = db.Column(db.Text, nullable=True)
    
    # Relationships
    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy=True)
    
    def __repr__(self):
        return f'<Achievement {self.title}>'
    
class FitnessLevelConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False,name='activity_type_id')
    
    fitness_level = db.Column(
        db.Enum('beginner', 'novice', 'intermediate', 'advanced', 'elite', name='fitnesslevelenum'),
        nullable=False
    )
    
    weight_ratio = db.Column(db.Float, nullable=True)  
    reps = db.Column(db.Integer, nullable=True) 
    sets = db.Column(db.Integer, nullable=True)  
    duration_minutes = db.Column(db.Float, nullable=True)  

    created_at = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f"<FitnessLevelConfig {self.fitness_level} - Activity {self.activity_type_id}>"


class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False,name='user_id')
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False,name='achievement_id')
    earned_at = db.Column(db.DateTime, default=func.now())
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id} - {self.achievement_id}>'
    


