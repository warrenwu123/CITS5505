import random
from app.models import ActivityType, FitnessLevelConfig,GoalType
from app.models import Goal, User, ActivitySession, Achievement, UserAchievement, Follow

def generate_weightloss_plan(goal):
    # activity type
    weightloss_activities = ActivityType.query.filter(
        ActivityType.name.in_(['Running', 'Cycling', 'Walking', 'Swimming'])
    ).all()

    if not weightloss_activities:
        raise Exception('Endurance activities not configured.')

    
    calorie_burn_rate = {
        'Running': 600,
        'Cycling': 500,
        'Walking': 300,
        'Swimming': 700
    }

    target_weight_loss_kg = goal.target_value
    total_calories_needed = target_weight_loss_kg * 7700  # 1kg fat ≈ 7700kcal

    
    total_minutes_per_week = goal.available_time_per_week * 60

    # assign the acivities to the available time
    total_calories_per_week = 0
    for activity in weightloss_activities:
        total_calories_per_week += (calorie_burn_rate[activity.name] * goal.available_time_per_week / len(weightloss_activities))

    weeks_needed = total_calories_needed / total_calories_per_week
    weeks_needed = max(1, int(weeks_needed)) 

    minutes_per_activity = total_minutes_per_week / len(weightloss_activities)

    # generate the plan
    plan = []
    for activity in weightloss_activities:
        burn_per_minute = calorie_burn_rate[activity.name] / 60
        plan.append({
            'activity': activity.name,
            'activity_type_id': activity.id,
            'target_minutes_per_week': round(minutes_per_activity, 1),
            'calories_burned': calorie_burn_rate[activity.name],
            'expected_calories_burned_per_week': round(burn_per_minute * minutes_per_activity, 1),
        })

    return {
        'plan': plan,
        'estimated_weeks_to_goal': weeks_needed,
        'total_calories_to_burn': total_calories_needed
    }

def generate_strength_plan(goal):
    # strength_plan_type = GoalType.query.filter_by(name='Strength').first()
    strength_activities = [
            "Barbell Squat", "Bench Press", "Deadlift",
            "Chin-up", "Military Press", "Push-up",
        ]

    
    minutes_per_exercise = 10
    total_minutes_per_week = goal.available_time_per_week * 60
    rounds_per_week = total_minutes_per_week // (minutes_per_exercise * len(strength_activities))
    
    plan = []
    for activity_name in strength_activities:
        activity_type = ActivityType.query.filter_by(name=activity_name).first()
        if not activity_type:
            continue 

        config = FitnessLevelConfig.query.filter_by(
            activity_type_id=activity_type.id,
            fitness_level=goal.fitness_level
        ).first()
        if config:
            plan.append({
                'activity': activity_name,
                'activity_type_id': activity_type.id,
                'weight_ratio': config.weight_ratio,
                'sets': config.sets,
                'reps': config.reps,
                'rounds_per_week': rounds_per_week
            })
    return plan

def generate_weightgain_plan(goal):
    # strength_plan_type = GoalType.query.filter_by(name='Strength').first()
    strength_activities = [
            "Barbell Squat", "Bench Press", "Deadlift",
            "Chin-up", "Military Press", "Push-up",
        ]

    plan = []
    for activity in strength_activities:
        plan.append({
            'activity': activity.name,
            'weight_ratio': 0.4,  # Example weight ratio for weight gain
            'sets': 2,
            'reps': 10
        })
    
 
    recipe_recommendations = [

    ]
    
    return {
        'strength_training': plan,
        'nutrition_plan': recipe_recommendations
    }

def generate_endurance_plan(goal):
    endurance_plan_type = GoalType.query.filter_by(name='Endurance').first()
    endurance_activities = endurance_plan_type.activities
    
    total_minutes_per_week = goal.available_time_per_week * 60
    minutes_per_activity = total_minutes_per_week / len(endurance_activities)
    
    plan = []
    for activity in endurance_activities:
        config = FitnessLevelConfig.query.filter_by(
            activity_type_id=activity.id,
            fitness_level=goal.fitness_level
        ).first()

        if config:
            plan.append({
                'activity': activity.name,
                'target_minutes': minutes_per_activity,
                'expected_speed_kmph': config.weight_ratio  # Example speed ratio for endurance
            })
    return plan