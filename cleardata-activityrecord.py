from app import app, db
from app.models import ActivityType, GoalType, FitnessLevelConfig
from app.models import ActivitySession, ActivityRecord

with app.app_context():
     db.session.query(ActivityRecord).delete()
     print("[DEBUG] All activity records deleted.")

     db.session.commit()