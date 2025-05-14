from app import app, db
from app.models import ActivityType, GoalType, FitnessLevelConfig,Goal
from app.models import ActivitySession, ActivityRecord

with app.app_context():
      db.session.query(Goal).delete()
      print("[DEBUG] All goals deleted.")

      db.session.commit()