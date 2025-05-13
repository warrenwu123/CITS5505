from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy import text

from app import db
from app.models import User, Goal, ActivityType, ActivitySession, Achievement, UserAchievement, Follow, GoalType,ActivityRecord
from app.dashboard import dashboard_bp
from app.util import generate_weightloss_plan,generate_strength_plan, generate_weightgain_plan, generate_endurance_plan

import datetime

@dashboard_bp.route('/')
@login_required
def index():
    """User dashboard page - main entry point"""
    return render_template('dashboard/index.html')

@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile section of the dashboard"""
    return render_template('dashboard/profile.html')

@dashboard_bp.route('/goals')
@login_required
def goals():
    """User goals section of the dashboard"""
    # Get user's goals
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    # Get all activity types for goal creation
    activity_types = ActivityType.query.all()
    print([atype.to_dict() for atype in activity_types])

    incomplete_sessions = ActivitySession.query.filter_by(user_id=current_user.id, is_completed=False).all()
    print([atype.to_dict() for atype in incomplete_sessions])

    from collections import defaultdict

    goal_types = GoalType.query.all()
    goal_type_map = {gt.id: gt.name for gt in goal_types}

    
    grouped_sessions = defaultdict(list)
    for session in incomplete_sessions:
        goal_type_id = session.goal_type_id
        if goal_type_id in goal_type_map:
            goal_type_name = goal_type_map[goal_type_id]
            grouped_sessions[goal_type_name].append(session)
        else:
            grouped_sessions['Unknown'].append(session)
    
    return render_template('dashboard/goals.html', goals=user_goals, activity_types=activity_types,sessions=incomplete_sessions,grouped_sessions=grouped_sessions)

@dashboard_bp.route('/achievements')
@login_required
def achievements():
    """User achievements section of the dashboard"""
    # Get user's earned achievements
    user_achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
    # Get all possible achievements
    all_achievements = Achievement.query.all()
    
    earned_ids = [ua.achievement_id for ua in user_achievements]
    unearned_achievements = [a for a in all_achievements if a.id not in earned_ids]
    
    return render_template('dashboard/achievements.html', 
                           user_achievements=user_achievements,
                           unearned_achievements=unearned_achievements,
                           all_achievements=all_achievements)

@dashboard_bp.route('/leaderboard')
@login_required
def leaderboard():
    """Leaderboard section of the dashboard"""
    # Get top users by activity count
    top_users_by_activity = db.session.query(
        User, func.count(ActivitySession.id).label('activity_count')
    ).join(ActivitySession, User.id == ActivitySession.user_id)\
     .group_by(User.id)\
     .order_by(func.count(ActivitySession.id).desc())\
     .limit(10).all()
    
    # Get top users by achievement count
    top_users_by_achievements = db.session.query(
        User, func.count(UserAchievement.id).label('achievement_count')
    ).join(UserAchievement, User.id == UserAchievement.user_id)\
     .group_by(User.id)\
     .order_by(func.count(UserAchievement.id).desc())\
     .limit(10).all()
    
    return render_template('dashboard/leaderboard.html',
                           top_users_by_activity=top_users_by_activity,
                           top_users_by_achievements=top_users_by_achievements)

@dashboard_bp.route('/explore')
@login_required
def explore():
    """Explore section of the dashboard with map"""
    return render_template('dashboard/explore.html')

@dashboard_bp.route('/social')
@login_required
def social():
    """Social interactions section of the dashboard (followers/following)"""
    # Get user's followers
    followers = db.session.query(User)\
        .join(Follow, Follow.follower_id == User.id)\
        .filter(Follow.followed_id == current_user.id)\
        .all()
    
    # Get users that the current user follows
    following = db.session.query(User)\
        .join(Follow, Follow.followed_id == User.id)\
        .filter(Follow.follower_id == current_user.id)\
        .all()
    
    # Get user suggestions (not following and not current user)
    user_suggestions = db.session.query(User)\
        .filter(User.id != current_user.id)\
        .filter(~User.id.in_([u.id for u in following]))\
        .limit(5)\
        .all()
    
    return render_template('dashboard/social.html',
                           followers=followers,
                           following=following,
                           user_suggestions=user_suggestions)

# API endpoints for dashboard functionality

@dashboard_bp.route('/api/create-goal', methods=['POST'])
@login_required
def create_goal():
    print("Available goal types in DB:",[atype.to_dict() for atype in GoalType.query.all()])
    """API endpoint to create a new goal"""
    data = request.json

    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    try:
        goal_type = data.get('goal_type')
        goal_type_obj = GoalType.query.filter_by(name=goal_type).first()
        if not goal_type_obj:
            return jsonify({'success': False, 'message': 'Invalid goal type'}), 400
        
        goal = Goal(
            user_id=current_user.id,
            goal_type_id=goal_type_obj.id,
            target_value=data.get('target_value'),
            fitness_level=data.get('fitness_level'),
            available_time_per_week = data.get('available_time_per_week'),
            start_date=func.now(),
            end_date = datetime.datetime.strptime(data.get('end_date'), '%Y-%m-%d').date(),
            is_completed=False
        )
        

        if goal_type == 'weightloss':
            plan = generate_weightloss_plan(goal)   
        elif goal_type == 'strength':
            plan = generate_strength_plan(goal)
        elif goal_type == 'weightgain':
            plan = generate_weightgain_plan(goal)
        elif goal_type == 'endurance':
            plan = generate_endurance_plan(goal)
        else:
            return jsonify({'error': 'Unsupported goal type'}), 400
        sessions = []
        
        if goal_type == 'strength' or goal_type == 'weightgain':
            
            for p in plan['strength_training'] if goal_type == 'weightgain' else plan:
                session = ActivitySession(
                    user_id=current_user.id,
                    activity_type_id=p.get('activity_type_id') if p.get('activity_type_id') else ActivityType.query.filter_by(name=p['activity']).first().id,
                    goal_id=goal.id,
                    goal_type_id=goal.goal_type_id,
                    start_time=datetime.now(),
                    duration=10 * p['rounds_per_week'],
                    reps=p.get('reps'),
                    sets=p.get('sets'),
                    calories_burned=None,
                    notes=None,
                    is_completed=False
                )
                sessions.append(session)

        elif goal_type == 'endurance' or goal_type == 'weightloss':
            for p in plan['plan']:
                session = ActivitySession(
                    user_id=current_user.id,
                    activity_type_id=p.get('activity_type_id') if p.get('activity_type_id') else ActivityType.query.filter_by(name=p['activity']).first().id,
                    goal_id=goal.id,
                    goal_type_id=goal.goal_type_id,
                    start_time=datetime.now(),
                    duration=p.get('target_minutes_per_week'),
                    calories_burned=p.get('expected_calories_burned_per_week'),
                    notes=None,
                    is_completed=False,
                )
                sessions.append(session)
        
        db.session.add(goal)
        db.session.commit()
        db.session.add_all(sessions)
        db.session.commit()

        sessions_data = ActivitySession.query.filter_by(user_id=current_user.id, goal_id=goal.id).all()
        
        return jsonify({'success': True, 'message': 'Goal created successfully', 'sessions': [session.to_dict() for session in sessions_data]})
        
    except Exception as e:
        import traceback
        traceback.print_exc()  
        return jsonify({'error': str(e)}), 500

        

@dashboard_bp.route('/api/update-goal-session', methods=['POST'])
def update_goal_session():
    data = request.get_json()

    session_id = data.get('session_id')
    reps = data.get('reps')
    sets = data.get('sets')
    duration = data.get('duration')

    if not session_id:
        return jsonify({'message': 'Session ID is required'}), 400

    session = ActivitySession.query.get(session_id)
    if not session:
        return jsonify({'message': 'Session not found'}), 404

    
    if reps is not None:
        session.reps = reps
    if sets is not None:
        session.sets = sets
    if duration is not None:
        session.duration = duration 

    try:
        db.session.commit()
        return jsonify({'message': 'Session updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update session', 'error': str(e)}), 500

@dashboard_bp.route('/api/sessions/<int:session_id>', methods=['DELETE'])
@login_required
def delete_activity_session(session_id):
    session = ActivitySession.query.get(session_id)

    if not session:
        return jsonify({"error": "Activity session not found."}), 404

    
    if session.goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized to delete this session."}), 403

    try:
        db.session.delete(session)
        db.session.commit()
        return jsonify({"message": "Activity session deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@dashboard_bp.route('/api/goals/delete/<int:goal_id>', methods=['DELETE'])
def delete_all_goals(goal_id):
    if not goal_id:
        return jsonify({"error": "Goal ID is required."}), 400
    try:
        Goal.query.filter_by(user_id=current_user.id,id=goal_id).delete()
        db.session.commit()
        
        return jsonify({"message": "All goals deleted and ID reset."}), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500
    
@dashboard_bp.route('/api/session_distribution', methods=['GET'])
@login_required
def session_distribution():

    goal_id = request.args.get('goal_id', type=int)
    
    if goal_id is None:
        return jsonify({'error': 'Missing goal_id parameter'}), 400
    
    results = (
        db.session.query(ActivityType.name, func.count(ActivitySession.id))
        .join(ActivitySession, ActivitySession.activity_type_id == ActivityType.id)
        .filter(ActivitySession.user_id == current_user.id)
        .filter(ActivitySession.goal_id == goal_id)
        .group_by(ActivityType.name)
        .all()
    )
    labels = [r[0] for r in results]
    data = [r[1] for r in results]
    return jsonify({'labels': labels, 'data': data})

from datetime import datetime, timedelta
from collections import defaultdict
@dashboard_bp.route('/api/activity_chart_data', methods=['GET'])
@login_required
def get_activity_chart_data():
    today = datetime.today().date()
    start_date = today - timedelta(days=6)

    records = (
        db.session.query(ActivityRecord, ActivitySession, ActivityType)
        .join(ActivitySession, ActivityRecord.session_id == ActivitySession.id)
        .join(ActivityType, ActivitySession.activity_type_id == ActivityType.id)
        .filter(ActivitySession.user_id == current_user.id)
        .filter(ActivityRecord.timestamp >= start_date)
        .all()
    )

    duration_activities = {"Running", "Walking", "Cycling", "Swimming"}
    reps_activities = {
        "Barbell Squat", "Bench Press", "Deadlift",
        "Chin-up", "Military Press", "Push-up"
    }

    date_labels = [(start_date + timedelta(days=i)).strftime('%a, %b %d') for i in range(7)]
    activity_data = defaultdict(lambda: [0] * 7)

    for record, session, activity_type in records:
        activity_name = activity_type.name
        timestamp_date = record.timestamp.date()
        day_index = (timestamp_date - start_date).days

        if 0 <= day_index < 7:
            if activity_name in duration_activities and record.actual_duration:
                activity_data[activity_name][day_index] += record.actual_duration
            elif activity_name in reps_activities and record.actual_reps:
                activity_data[activity_name][day_index] += record.actual_reps

    colors = {
        "Running": ('rgba(78, 115, 223, 0.5)', 'rgba(78, 115, 223, 1)'),
        "Cycling": ('rgba(28, 200, 138, 0.5)', 'rgba(28, 200, 138, 1)'),
        "Walking": ('rgba(133, 135, 150, 0.5)', 'rgba(133, 135, 150, 1)'),
        "Swimming": ('rgba(231, 74, 59, 0.5)', 'rgba(231, 74, 59, 1)'),
        "Barbell Squat": ('rgba(54, 185, 204, 0.5)', 'rgba(54, 185, 204, 1)'),
        "Bench Press": ('rgba(246, 194, 62, 0.5)', 'rgba(246, 194, 62, 1)'),
        "Deadlift": ('rgba(90, 92, 105, 0.5)', 'rgba(90, 92, 105, 1)'),
        "Chin-up": ('rgba(58, 123, 213, 0.5)', 'rgba(58, 123, 213, 1)'),
        "Military Press": ('rgba(100, 181, 246, 0.5)', 'rgba(100, 181, 246, 1)'),
        "Push-up": ('rgba(255, 99, 132, 0.5)', 'rgba(255, 99, 132, 1)')
    }

    datasets = []
    for activity, data_points in activity_data.items():
        bg_color, border_color = colors.get(activity, ('rgba(100,100,100,0.5)', 'rgba(100,100,100,1)'))
        datasets.append({
            "label": activity,
            "data": data_points,
            "backgroundColor": bg_color,
            "borderColor": border_color,
            "borderWidth": 1
        })

    return jsonify({
        "labels": date_labels,
        "datasets": datasets
    })

@dashboard_bp.route('/api/log-activity', methods=['POST'])
@login_required
def log_activity():
    """API endpoint to log a new activity session"""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    try:
        activity_session = ActivitySession(
            user_id=current_user.id,
            activity_type_id=data.get('activity_type_id'),
            start_time=data.get('start_time', func.now()),
            end_time=data.get('end_time'),
            distance=data.get('distance'),
            reps=data.get('reps'),
            duration=data.get('duration'),
            calories_burned=data.get('calories_burned'),
            notes=data.get('notes')
        )
        
        db.session.add(activity_session)
        db.session.commit()
        
        # Check if this activity completes any goals
        check_goals_completion(current_user.id, activity_session.activity_type_id)
        
        # Check if user earned any achievements
        check_achievements(current_user.id)
        
        return jsonify({'success': True, 'message': 'Activity logged successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@dashboard_bp.route('/api/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    """API endpoint to follow another user"""
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot follow yourself'}), 400
    
    user_to_follow = User.query.get(user_id)
    
    if not user_to_follow:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    if current_user.is_following(user_to_follow):
        return jsonify({'success': False, 'message': 'You are already following this user'}), 400
    
    try:
        current_user.follow(user_to_follow)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'You are now following {user_to_follow.email}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@dashboard_bp.route('/api/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    """API endpoint to unfollow another user"""
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot unfollow yourself'}), 400
    
    user_to_unfollow = User.query.get(user_id)
    
    if not user_to_unfollow:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    if not current_user.is_following(user_to_unfollow):
        return jsonify({'success': False, 'message': 'You are not following this user'}), 400
    
    try:
        current_user.unfollow(user_to_unfollow)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'You have unfollowed {user_to_unfollow.email}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

from sqlalchemy.exc import SQLAlchemyError
@dashboard_bp.route('/dashboard/api/sessions/<int:session_id>/complete', methods=['POST'])
def complete_session(session_id):
    data = request.get_json()
    per_round = data.get('per_round', 0)

    try:
        session = ActivitySession.query.get(session_id)
        if not session:
            return jsonify({'message': 'Session not found'}), 404

        if per_round > 0:
            # 减少 duration，防止负值
            session.duration = max(session.duration - per_round, 0)

        # 如果 duration 减为 0，标记为完成
        if session.duration == 0:
            session.is_completed = True

        db.session.commit()
        return jsonify({'message': 'Session updated successfully'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'error': str(e)}), 500

# Helper functions

def check_goals_completion(user_id, activity_type_id):
    """Check if an activity has completed any of the user's goals"""
    goals = Goal.query.filter_by(
        user_id=user_id,
        activity_type_id=activity_type_id,
        is_completed=False
    ).all()
    
    for goal in goals:
        progress = goal.get_progress()
        if progress >= 100:
            goal.is_completed = True
    
    db.session.commit()

def check_achievements(user_id):
    """Check if user has earned any new achievements"""
    # Get all achievements not yet earned by the user
    earned_achievement_ids = db.session.query(UserAchievement.achievement_id)\
        .filter(UserAchievement.user_id == user_id).all()
    
    earned_ids = [id[0] for id in earned_achievement_ids]
    
    unearned_achievements = Achievement.query.filter(
        ~Achievement.id.in_(earned_ids) if earned_ids else True
    ).all()
    
    # For each unearned achievement, check if the user meets the requirements
    for achievement in unearned_achievements:
        # First Activity Achievement
        if achievement.title == "First Activity":
            activity_count = ActivitySession.query.filter_by(
                user_id=user_id, 
                is_completed=True
            ).count()
            
            if activity_count >= 1:
                award_achievement(user_id, achievement.id)
        
        # First Goal Completion Achievement
        elif achievement.title == "Goal Crusher":
            completed_goals = Goal.query.filter_by(
                user_id=user_id, 
                is_completed=True
            ).count()
            
            if completed_goals >= 1:
                award_achievement(user_id, achievement.id)
        
        # Training Time Achievement (1+ hour)
        elif achievement.title == "Hour Trainer":
            # Sum of all completed session durations
            total_duration = db.session.query(func.sum(ActivitySession.duration))\
                .filter(
                    ActivitySession.user_id == user_id,
                    ActivitySession.is_completed == True
                ).scalar() or 0

            print("Total Duration:", total_duration)
            
            if total_duration >= 60:  # 60 minutes = 1 hour
                award_achievement(user_id, achievement.id)
        
        # Calorie Burner Achievement (1000+ calories)
        elif achievement.title == "Calorie Burner":
            # Sum of calories burned across all completed sessions
            total_calories = db.session.query(func.sum(ActivitySession.calories_burned))\
                .filter(
                    ActivitySession.user_id == user_id,
                    ActivitySession.is_completed == True
                ).scalar() or 0
            
            if total_calories >= 1000:
                award_achievement(user_id, achievement.id)
        
        # Activity Streak Achievement (5 consecutive days)
        elif achievement.title == "Activity Streak":
            # Get all completed activity sessions ordered by date
            completed_sessions = ActivitySession.query.filter_by(
                user_id=user_id,
                is_completed=True
            ).order_by(ActivitySession.start_time).all()
            
            if completed_sessions:
                # Extract dates and remove time component
                session_dates = [session.start_time.date() for session in completed_sessions]
                # Remove duplicates (multiple activities on same day)
                unique_dates = sorted(set(session_dates))
                
                # Check for streak of 5 consecutive days
                max_streak = 1
                current_streak = 1
                for i in range(1, len(unique_dates)):
                    # If dates are consecutive
                    if (unique_dates[i] - unique_dates[i-1]).days == 1:
                        current_streak += 1
                        max_streak = max(max_streak, current_streak)
                    else:
                        current_streak = 1
                print("Max Streak:", max_streak)
                if max_streak >= 5:  # 5-day streak
                    award_achievement(user_id, achievement.id)
        
        # Strength Training Achievement (focused on strength exercises)
        elif achievement.title == "Strength Enthusiast":
            # Get IDs of strength-related activity types
            strength_activity_ids = db.session.query(ActivityType.id)\
                .filter(ActivityType.name.in_(['Weightlifting', 'Push-ups', 'Pull-ups', 'Squats', 'Deadlifts']))\
                .all()
            
            strength_ids = [id[0] for id in strength_activity_ids]
            
            if strength_ids:
                # Count strength training sessions
                strength_sessions = ActivitySession.query.filter(
                    ActivitySession.user_id == user_id,
                    ActivitySession.is_completed == True,
                    ActivitySession.activity_type_id.in_(strength_ids)
                ).count()
                
                if strength_sessions >= 5:  # 5+ strength sessions
                    award_achievement(user_id, achievement.id)
        
        # Cardio Master Achievement (focused on cardio exercises)
        elif achievement.title == "Cardio Master":
            # Get IDs of cardio-related activity types
            cardio_activity_ids = db.session.query(ActivityType.id)\
                .filter(ActivityType.name.in_(['Running', 'Cycling', 'Swimming', 'Jumping Rope', 'HIIT']))\
                .all()
            
            cardio_ids = [id[0] for id in cardio_activity_ids]
            
            if cardio_ids:
                # Count cardio sessions
                cardio_sessions = ActivitySession.query.filter(
                    ActivitySession.user_id == user_id,
                    ActivitySession.is_completed == True,
                    ActivitySession.activity_type_id.in_(cardio_ids)
                ).count()
                
                if cardio_sessions >= 5:  # 5+ cardio sessions
                    award_achievement(user_id, achievement.id)

def award_achievement(user_id, achievement_id):
    """Award an achievement to a user"""
    # Check if the user already has this achievement
    existing = UserAchievement.query.filter_by(
        user_id=user_id,
        achievement_id=achievement_id
    ).first()
    
    if existing:
        return
    
    user_achievement = UserAchievement(
        user_id=user_id,
        achievement_id=achievement_id,
        earned_at=func.now()
    )
    
    db.session.add(user_achievement)
    db.session.commit()


def check_goal_progress(goal_id):
    """Check if a goal is completed based on its associated sessions"""
    if not goal_id:
        return
        
    goal = Goal.query.get(goal_id)
    if not goal:
        return
        
    # Get progress
    progress = goal.get_progress()
    
    # Update goal completion status if progress is 100%
    if progress["percentage"] >= 100 and not goal.is_completed:
        goal.is_completed = True
        db.session.commit()