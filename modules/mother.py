from flask import Blueprint, render_template, session, redirect, url_for, request
import sqlite3
from datetime import datetime
from modules.mother_module import (
    calculate_pregnancy_info,
    get_health_tip,
    log_mood,
    check_danger_signs  # Imported function
)
from flask import flash
import smtplib
from email.mime.text import MIMEText


mother_bp = Blueprint("mother", __name__, template_folder="../templates/mother")

# ------------------ Mother Dashboard ------------------ #
@mother_bp.route("/mother/index")
def index():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    username = session['username']
    conn = sqlite3.connect("data/usalama.db")
    cursor = conn.cursor()
    cursor.execute("SELECT due_date, id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return "Due date not found. Please contact support."

    due_date_str = row[0]
    user_id = row[1]

    pregnancy_info = calculate_pregnancy_info(due_date_str)
    week = pregnancy_info['week_number']
    health_tip = get_health_tip(week)

    return render_template("mother_index.html",
                           username=username,
                           pregnancy_info=pregnancy_info,
                           health_tip=health_tip)

# ------------------ Mood Tracking ------------------ #
@mother_bp.route("/mother/track_mood", methods=['GET', 'POST'])
def track_mood():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    username = session['username']

    if request.method == 'POST':
        mood = request.form.get('mood')
        if not mood:
            return render_template("track_mood.html", error="Please select a mood.")

        conn = sqlite3.connect("data/usalama.db")
        sql = conn.cursor()
        sql.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = sql.fetchone()
        conn.close()

        if row:
            user_id = row[0]
            log_mood(user_id, mood)
            return render_template("success.html", message="Mood logged successfully.", back_url=url_for('mother.index'))


    return render_template("track_mood.html")

# ------------------ Audio Tips ------------------ #
@mother_bp.route("/mother/audio_tips")
def audio_tips():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute("SELECT file_path, tip_type, language FROM audio_tips")
    audio_data = sql.fetchall()
    conn.close()

    return render_template("audio_tips.html", audio_tips=audio_data)

# ------------------ Danger Sign Checker ------------------ #
from flask import flash
import smtplib
from email.mime.text import MIMEText

PARTNER_EMAIL = "partner@example.com"

def send_partner_notification(symptoms_found):
    body = f"Emergency alert! Danger signs detected: {', '.join(symptoms_found)}"
    msg = MIMEText(body)
    msg['Subject'] = "Urgent: Danger Signs Detected"
    msg['From'] = "noreply@usalamaapp.com"
    msg['To'] = PARTNER_EMAIL

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('your_email@gmail.com', 'your_password')  # Use env vars for security
            server.send_message(msg)
    except Exception as e:
        print("Error sending notification:", e)

@mother_bp.route("/mother/check_danger_signs", methods=['GET', 'POST'])
def check_danger_signs_route():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    results = {}
    emergency_flag = False
    emergency_symptoms = []

    if request.method == 'POST':
        symptoms_input = request.form.get('symptoms', '')
        symptoms = [s.strip().lower() for s in symptoms_input.split(',') if s.strip()]

        results = check_danger_signs(symptoms)

        if results:
            emergency_flag = True
            emergency_symptoms = list(results.keys())
            send_partner_notification(emergency_symptoms)
            flash("Emergency flagged! Partner has been notified.", "danger")
        else:
            flash("No danger signs detected.", "success")

    return render_template("check_danger_signs.html", results=results)

