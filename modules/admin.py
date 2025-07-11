# modules/admin.py

from flask import Blueprint, render_template, request, redirect, session, url_for, current_app
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# ------------- Helper to check login -------------
def login_required(role):
    def wrapper(func):
        def decorated_view(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('auth.login'))
            return func(*args, **kwargs)
        decorated_view.__name__ = func.__name__
        return decorated_view
    return wrapper

# ------------- Admin Dashboard -------------
@admin_bp.route('/admindashboard')
@login_required('admin')
def admin_dashboard():
    return render_template("admin_dashboard.html", username=session['username'])

# ------------- View All Users -------------
@admin_bp.route('/admin/users')
@login_required('admin')
def admin_users():
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute("SELECT id, full_name, username, email, phone, role FROM users")
    users = sql.fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

# ------------- System Reports -------------
@admin_bp.route('/admin/reports')
@login_required('admin')
def admin_reports():
    conn = sqlite3.connect("data/usalama.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    user_summary = cursor.fetchall()
    cursor.execute("SELECT username, failed_attempts FROM login_attempts ORDER BY failed_attempts DESC")
    login_activity = cursor.fetchall()
    conn.close()
    return render_template("admin_reports.html", user_summary=user_summary, login_activity=login_activity)

# ------------- View Text Tips -------------
@admin_bp.route('/admin/view_tips')
@login_required('admin')
def view_tips():
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute('SELECT id, tip_type, week_number, keyword, language, content FROM text_tips')
    tips = sql.fetchall()
    conn.close()
    return render_template("view_tips.html", tips=tips)

# ------------- Add Text Tip -------------
@admin_bp.route('/admin/add_tip', methods=['GET', 'POST'])
@login_required('admin')
def add_tip():
    if request.method == 'POST':
        tip_type = request.form['tip_type']
        week_number = request.form.get('week_number')
        keyword = request.form.get('keyword')
        language = request.form['language']
        content = request.form['content']

        conn = sqlite3.connect("data/usalama.db")
        sql = conn.cursor()
        sql.execute('''
            INSERT INTO text_tips (tip_type, week_number, keyword, language, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (tip_type, week_number, keyword, language, content))
        conn.commit()
        conn.close()

        return render_template("success.html", message="Health tip uploaded successfully!")
    
    return render_template("add_tip.html")

# ------------- Upload Audio Tips -------------
@admin_bp.route('/admin/upload_audio', methods=['GET', 'POST'])
@login_required('admin')
def upload_audio():
    if request.method == 'POST':
        tip_type = request.form['tip_type']
        week_number = request.form.get('week_number')
        keyword = request.form.get('keyword')
        language = request.form['language']
        audio_file = request.files['audio_file']

        if audio_file and allowed_file(audio_file.filename):
            filename = secure_filename(audio_file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(save_path)

            conn = sqlite3.connect("data/usalama.db")
            sql = conn.cursor()
            sql.execute('''
                INSERT INTO audio_tips (tip_type, week_number, keyword, language, file_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (tip_type, week_number, keyword, language, filename))
            conn.commit()
            conn.close()

            return render_template("success.html", message="Audio tip uploaded successfully.")
        else:
            return "Invalid file format. Please upload .mp3 or .wav only."

    return render_template("upload_audio.html")

# ------------- View Uploaded Audio Tips -------------
@admin_bp.route('/admin/view_audio')
@login_required('admin')
def view_audio():
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute('SELECT id, tip_type, week_number, keyword, language, file_path FROM audio_tips')
    audio_tips = sql.fetchall()
    conn.close()
    return render_template("view_audio.html", audio_tips=audio_tips)

# ------------- Audio File Checker -------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav'}
