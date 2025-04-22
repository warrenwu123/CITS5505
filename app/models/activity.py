import datetime
from app import db
from sqlalchemy.sql import func

class ActivityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    
    # Relationships
    activity_sessions = db.relationship('ActivitySession', backref='activity_type', lazy=True)
    goals = db.relationship('Goal', backref='activity_type', lazy=True)
    
    def __repr__(self):
        return f'<ActivityType {self.name}>'


class ActivitySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=func.now())
    end_time = db.Column(db.DateTime, nullable=True)
    distance = db.Column(db.Float, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Interval, nullable=True)
    calories_burned = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<ActivitySession {self.id}>'


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


class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=func.now())
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id} - {self.achievement_id}>'


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # distance, duration, reps, etc.
    target_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=func.now())
    end_date = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Goal {self.goal_type} {self.target_value}>'
        
    def get_progress(self):
        """Calculate progress towards goal based on activity sessions"""
        from sqlalchemy import func
        
        # Query to sum up activity metrics based on goal type
        if self.end_date is None or self.end_date > datetime.datetime.utcnow():
            query = ActivitySession.query.filter(
                ActivitySession.user_id == self.user_id,
                ActivitySession.activity_type_id == self.activity_type_id,
                ActivitySession.start_time >= self.start_date
            )
            
            if self.goal_type == 'distance':
                total = db.session.query(func.sum(ActivitySession.distance)).filter(
                    ActivitySession.user_id == self.user_id,
                    ActivitySession.activity_type_id == self.activity_type_id,
                    ActivitySession.start_time >= self.start_date
                ).scalar() or 0
                
            elif self.goal_type == 'duration':
                # Convert interval to seconds for calculation
                total = db.session.query(
                    func.sum(func.extract('epoch', ActivitySession.duration))
                ).filter(
                    ActivitySession.user_id == self.user_id,
                    ActivitySession.activity_type_id == self.activity_type_id,
                    ActivitySession.start_time >= self.start_date
                ).scalar() or 0
                
            elif self.goal_type == 'reps':
                total = db.session.query(func.sum(ActivitySession.reps)).filter(
                    ActivitySession.user_id == self.user_id,
                    ActivitySession.activity_type_id == self.activity_type_id,
                    ActivitySession.start_time >= self.start_date
                ).scalar() or 0
                
            elif self.goal_type == 'calories':
                total = db.session.query(func.sum(ActivitySession.calories_burned)).filter(
                    ActivitySession.user_id == self.user_id,
                    ActivitySession.activity_type_id == self.activity_type_id,
                    ActivitySession.start_time >= self.start_date
                ).scalar() or 0
            
            else:
                total = 0
                
            # Calculate percentage
            if self.target_value > 0:
                percentage = min(100, (total / self.target_value) * 100)
            else:
                percentage = 0
                
            # Update is_completed if goal is met
            if percentage >= 100 and not self.is_completed:
                self.is_completed = True
                db.session.commit()
                
            return {
                'current': total,
                'target': self.target_value,
                'percentage': percentage,
                'is_completed': self.is_completed
            }
        
        return {
            'current': 0,
            'target': self.target_value,
            'percentage': 0,
            'is_completed': self.is_completed
        }