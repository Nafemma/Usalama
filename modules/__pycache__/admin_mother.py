# admin mother_module.py
import json
import os
from utilities.data_loader import load_json_data

DATA_FILE ="data/health_tips.json";

def load_tips():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_tips(tips):
    with open(DATA_FILE, "w") as f:
        json.dump(tips, f, indent=2)

def add_tip(trimester, new_tip):
    tips = load_tips()
    if trimester not in tips:
        tips[trimester] = {"tips": []}
    tips[trimester]["tips"].append(new_tip)
    save_tips(tips)

def update_tip(trimester, index, updated_tip):
    tips = load_tips()
    if trimester in tips and 0 <= index < len(tips[trimester]["tips"]):
        tips[trimester]["tips"][index] = updated_tip
        save_tips(tips)

def delete_tip(trimester, index):
    tips = load_tips()
    if trimester in tips and 0 <= index < len(tips[trimester]["tips"]):
        del tips[trimester]["tips"][index]
        save_tips(tips)
