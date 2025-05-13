from app import create_app, db
from app.models import User, ActivitySession
from sqlalchemy import func

def update_user_total_duration():
    """Update total_duration for all users based on their activity sessions"""
    app = create_app()
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        for user in users:
            # Calculate total duration from completed activity sessions
            total_duration = db.session.query(func.sum(ActivitySession.duration))\
                .filter(ActivitySession.user_id == user.id)\
                .filter(ActivitySession.is_completed == True)\
                .scalar() or 0
            
            # Update user's total_duration
            user.total_duration = total_duration
            print(f"Updated user {user.email}: total_duration = {total_duration}")
        
        # Commit all changes
        db.session.commit()
        print("Successfully updated all users' total duration")

if __name__ == "__main__":
    update_user_total_duration() 