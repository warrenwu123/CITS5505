from app import create_app, db
from app.models import User
from app.dashboard.routes import check_achievements

def update_all_user_achievements():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        for user in users:
            check_achievements(user.id)
            print(f"Checked achievements for {user.email}")
        print("All users' achievements updated.")

if __name__ == "__main__":
    update_all_user_achievements() 