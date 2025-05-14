from app import app, db
from app.models import ActivityType, GoalType, FitnessLevelConfig,Achievement
from app.models import ActivitySession, ActivityRecord

with app.app_context():
     db.session.query(Achievement).delete()
     print("[DEBUG] All activity records deleted.")

     db.session.commit()