# modules/mother.py

from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3

mother_bp = Blueprint('mother', __name__)

# ----------- Mother Dashboard (Index) -----------
@mother_bp.route('/motherindex')
def mother_index():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect("data/usalama.db")
    cursor = conn.cursor()
    
    # Fetch user's language preference
    cursor.execute("SELECT language FROM users WHERE username = ?", (session['username'],))
    lang_result = cursor.fetchone()
    user_language = lang_result[0] if lang_result else 'english'
    
    # Fetch tips grouped by trimester for that language
    cursor.execute("""
        SELECT trimester, group_concat(tip_text, '|||') 
        FROM trimester_tips 
        WHERE language = ?
        GROUP BY trimester
    """, (user_language,))
    
    tips_data = cursor.fetchall()
    conn.close()
    
    # Format tips into a dict: {'first': [...], 'second': [...], 'third': [...]}
    tips = {}
    for trimester, tip_concat in tips_data:
        tips[trimester] = {
            "tips": tip_concat.split('|||') if tip_concat else []
        }
    
    return render_template("mother/index.html", 
                           username=session['username'],
                           tips=tips)
