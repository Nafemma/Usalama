# mother_module.py
<<<<<<< HEAD

import json
from datetime import datetime, timedelta
from utilities.data_loader import load_json_data

=======
import json
import random
from datetime import datetime, timedelta
from utilities.data_loader import load_json_data


>>>>>>> 44fb19b8e2d234b3d7afb125605a1b6e91564d97
# Load tips and danger signs from external files
TIPS = load_json_data("data/health_tips.json")
DANGER_SIGNS = load_json_data("data/danger_signs.json")

# 1. View Pregnancy Week
def calculate_pregnancy_info(start_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    today = datetime.today()
    days_passed = (today - start_date).days
    week_number = days_passed // 7

    if week_number < 13:
        trimester = "First Trimester"
    elif week_number < 27:
        trimester = "Second Trimester"
    else:
        trimester = "Third Trimester"

    due_date = start_date + timedelta(days=280)
    return {
        "week_number": week_number,
        "trimester": trimester,
        "due_date": due_date.strftime("%Y-%m-%d")
    }

# 2. Get Health Tip
<<<<<<< HEAD
def get_health_tip(week_number):
    tips = {int(k): v for k, v in TIPS.items()}
    for week in sorted(tips.keys(), reverse=True):
        if week_number >= week:
            return tips[week]
    return "Stay positive and follow medical advice."
=======
# def get_health_tip(week_number):
#     tips = {int(k): v for k, v in TIPS.items()}
#     for week in sorted(tips.keys(), reverse=True):
#         if week_number >= week:
#             return tips[week]
#     return "Stay positive and follow medical advice."

# Get a health tip based on the week number randomly selected from the trimester's tips
def get_health_tip(week_number):
    
    if week_number < 13:
        trimester = "First Trimester"
    elif week_number < 27:
        trimester = "Second Trimester"
    else:
        trimester = "Third Trimester"

    trimester_data = TIPS.get(trimester, {})
    tip_list = trimester_data.get("tips", [])

    if tip_list:
        return random.choice(tip_list)
    else:
        return "Stay positive and follow medical advice."

>>>>>>> 44fb19b8e2d234b3d7afb125605a1b6e91564d97

# 3. Log Mood
def log_mood(user_id, mood):
    path = f"data/mood_logs/{user_id}_moods.txt"
    with open(path, "a") as f:
        f.write(f"{datetime.now()} - Mood: {mood}\n")
    return f"Mood '{mood}' logged."

# 4. Danger Sign Checker
<<<<<<< HEAD
=======
# normalized the danger signs to handle case insensitivity and partial matches
# and added more detailed messages for each sign    
>>>>>>> 44fb19b8e2d234b3d7afb125605a1b6e91564d97
def check_danger_signs(symptoms):
    result = {}
    for symptom in symptoms:
        normalized = symptom.strip().lower()
<<<<<<< HEAD
        if normalized in DANGER_SIGNS:
            result[normalized] = DANGER_SIGNS[normalized]
    return result if result else "No danger signs found."



=======
        for danger_sign, info in DANGER_SIGNS.items():
            if normalized in danger_sign.lower() or danger_sign.lower() in normalized:
                result[danger_sign] = info
    return result if result else "No danger signs found."

>>>>>>> 44fb19b8e2d234b3d7afb125605a1b6e91564d97
# 5. Logout
def logout():
    return "You have been logged out. Stay healthy!"
