from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3
from datetime import datetime

partner_bp = Blueprint('partner', __name__)

@partner_bp.route('/partnerdashboard')
def partner_dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()

    # Get the mother's username linked to this partner
    sql.execute("SELECT linked_mother_username FROM users WHERE username = ?", (username,))
    row = sql.fetchone()
    linked_mother = row[0] if row else None

    mother_info = None
    tips = []
    moods = []
    symptoms = []
    audio_tips = []

    if linked_mother:
        # Fetch the mother's full info
        sql.execute("SELECT id, full_name, email, phone, due_date, language FROM users WHERE username = ?", (linked_mother,))
        mother_info = sql.fetchone()

        if mother_info:
            mother_id = mother_info[0]
            due_date_str = mother_info[4]
            language = mother_info[5]

            # Calculate pregnancy week
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                    today = datetime.now()
                    pregnancy_weeks = 40 - ((due_date - today).days // 7)

                    if 0 < pregnancy_weeks <= 40:
                        # Fetch weekly tips based on current week and language
                        sql.execute("""
                            SELECT tip_type, content FROM text_tips 
                            WHERE week_number = ? AND language = ?
                        """, (pregnancy_weeks, language))
                        tips = sql.fetchall()

                except Exception as e:
                    print("Date error:", e)

            # Fetch recent moods (last 5)
            # Fetch recent moods (last 5)
            sql.execute("""
            SELECT timestamp, mood FROM mood_logs
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT 5
            """, (linked_mother,))
            moods = sql.fetchall()

            # Fetch recent symptoms/danger signs (last 5)
            # Adjust table/column names if needed
           ###    WHERE user_id = ?
             #   ORDER BY reported_at DESC
             #   LIMIT 5
           # """, (mother_id,))
           # symptoms = sql.fetchall()

            # Fetch audio tips matching language
            sql.execute("""
                SELECT tip_type, file_path FROM audio_tips
                WHERE language = ?
                ORDER BY tip_type
            """, (language,))
            audio_tips = sql.fetchall()

    conn.close()

    return render_template("partner_dashboard.html",
                           linked_mother=linked_mother,
                           mother_info=mother_info,
                           tips=tips,
                           moods=moods,
                           symptoms=symptoms,
                           audio_tips=audio_tips)
