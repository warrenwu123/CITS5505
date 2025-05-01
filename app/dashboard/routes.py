from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import User, Goal, ActivityType, ActivitySession, Achievement, UserAchievement, Follow, GoalType
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
    
    return render_template('dashboard/goals.html', goals=user_goals, activity_types=activity_types,sessions=incomplete_sessions)

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
                           unearned_achievements=unearned_achievements)

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
            activity_type_id=data.get('activity_type_id'),
            goal_type_id=goal_type_obj.id,
            target_value=data.get('target_value'),
            fitness_level=data.get('fitness_level'),
            available_time_per_week = data.get('available_time_per_week'),
            start_date=func.now(),
            end_date=data.get('end_date'),
            is_completed=False
        )
        
        db.session.add(goal)
        db.session.commit()
       
        
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
        today = datetime.date.today()
        if goal_type == 'strength' or goal_type == 'weightgain':
            for p in plan['strength_training'] if goal_type == 'weightgain' else plan:
                session = ActivitySession(
                    user_id=current_user.id,
                    activity_type_id=p.get('activity_type_id') if p.get('activity_type_id') else ActivityType.query.filter_by(name=p['activity']).first().id,
                    goal_id=goal.id,
                    goal_type_id=goal.goal_type_id,
                    start_time=datetime.datetime.combine(today, datetime.time(9, 0)),  
                    duration=datetime.timedelta(minutes=10 * p['rounds_per_week']),
                    reps=p.get('reps'),
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
                    start_time=datetime.datetime.combine(today, datetime.time(7, 0)), 
                    duration=datetime.timedelta(minutes=p.get('target_minutes') or p.get('target_minutes_per_week')),
                    calories_burned=p.get('expected_calories_burned_per_week'),
                    notes=None,
                    is_completed=False
                )
                sessions.append(session)

        db.session.add_all(sessions)
        db.session.commit()

        sessions_data = ActivitySession.query.filter_by(user_id=current_user.id, goal_id=goal.id).all()
        
        return jsonify({'success': True, 'message': 'Goal created successfully', 'sessions': [session.to_dict() for session in sessions_data]})
        
    except Exception as e:
        import traceback
        traceback.print_exc()  
        return jsonify({'error': str(e)}), 500

        

@dashboard_bp.route('/api/update-goal/<int:goal_id>', methods=['PUT'])
@login_required
def update_goal(goal_id):
    """API endpoint to update a goal"""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    
    if not goal:
        return jsonify({'success': False, 'message': 'Goal not found'}), 404
    
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    try:
        if 'activity_type_id' in data:
            goal.activity_type_id = data.get('activity_type_id')
        if 'goal_type' in data:
            goal.goal_type = data.get('goal_type')
        if 'target_value' in data:
            goal.target_value = data.get('target_value')
        if 'end_date' in data:
            goal.end_date = data.get('end_date')
        if 'is_completed' in data:
            goal.is_completed = data.get('is_completed')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Goal updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@dashboard_bp.route('/api/delete-goal/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id):
    """API endpoint to delete a goal"""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    
    if not goal:
        return jsonify({'success': False, 'message': 'Goal not found'}), 404
    
    try:
        db.session.delete(goal)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Goal deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

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
        ~Achievement.id.in_(earned_ids)
    ).all()
    
    # For each unearned achievement, check if the user meets the requirements
    for achievement in unearned_achievements:
        # Here we would implement the logic to check achievement requirements
        # For now, this is placeholder logic
        if achievement.title == "First Activity":
            activity_count = ActivitySession.query.filter_by(user_id=user_id).count()
            if activity_count >= 1:
                award_achievement(user_id, achievement.id)
        
        elif achievement.title == "Activity Streak":
            # Check for 5 consecutive days of activity
            # This would require more complex date-based queries
            pass
        
        elif achievement.title == "Distance Champion":
            # Check if total distance exceeds a threshold
            total_distance = db.session.query(func.sum(ActivitySession.distance))\
                .filter(ActivitySession.user_id == user_id).scalar() or 0
            
            if total_distance >= 100:  # 100 kilometers for example
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