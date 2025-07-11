# modules/partner.py

from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3
from datetime import datetime

partner_bp = Blueprint('partner', __name__)

# ----------- Partner Dashboard -----------
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

    if linked_mother:
        # Fetch the mother's full info
        sql.execute("SELECT full_name, email, phone, due_date, language FROM users WHERE username = ?", (linked_mother,))
        mother_info = sql.fetchone()

        if mother_info:
            due_date_str = mother_info[3]
            language = mother_info[4]

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

    conn.close()

    return render_template("partner_dashboard.html",
                           linked_mother=linked_mother,
                           mother_info=mother_info,
                           tips=tips)
