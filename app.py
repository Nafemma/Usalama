# ------------ IMPORTS ------------
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3
import random
import smtplib
import os
from email.message import EmailMessage
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# ------------ FLASK CONFIG ------------
app = Flask(__name__)
app.secret_key = "usalama_secret"

# ------------ AUDIO CONFIG ------------
UPLOAD_FOLDER = 'audios'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------ EMAIL OTP FUNCTION ------------
def send_otp(email):
    otp = str(random.randint(100000, 999999))

import sqlite3  # For database operations
import random   # For generating OTP
import smtplib  # For sending OTP email
import os       # For file and path operations
from email.message import EmailMessage  # For formatting email messages
from modules.mother.admin_mother import load_tips, add_tip, update_tip, delete_tip
from modules.mother.mother_module import calculate_pregnancy_info, check_danger_signs, get_health_tip, log_mood
from werkzeug.utils import secure_filename  # For safe file names in uploads






# ------------ FLASK APP CONFIG ------------
app = Flask(__name__)
app.secret_key = "usalama_secret"  # Used to secure session data like OTP

# ------------ AUDIO UPLOAD CONFIG ------------
UPLOAD_FOLDER = 'audios'  # Custom audio folder
ALLOWED_EXTENSIONS = {'mp3', 'wav'}  # Only allow .mp3 and .wav formats
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

# Check if file has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------ OTP SENDING FUNCTION ------------
def send_otp(email):
    otp = str(random.randint(100000, 999999))  # Generate random 6-digit OTP

    session['otp'] = otp
    session['email'] = email

    sender = 'mpofuemmanuellah@gmail.com'
    app_password = 'fvwm rifq nquu nunk'
    subject = "Usalama OTP Verification"
    body = f"Your Usalama verification code is: {otp}"

    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = email
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False

# ------------ REGISTRATION ------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

# ------------ REGISTRATION + OTP VERIFICATION ------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Store form inputs in session for temporary use

        session['full_name'] = request.form['full_name']
        session['username'] = request.form['username']
        session['email'] = request.form['email']
        session['phone'] = request.form['phone']
        session['password'] = request.form['password']
        session['role'] = request.form['role']
        session['due_date'] = request.form.get('due_date')
        session['language'] = request.form['language']
        session['linked_mother_username'] = request.form.get('linked_mother_username')


        # Send OTP
        if send_otp(session['email']):
            return redirect(url_for('verify_otp'))
        else:
            return "Failed to send OTP. Try again."

    return render_template("register.html")

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        if request.form['otp'] == session.get('otp'):
            try:
                conn = sqlite3.connect("data/usalama.db")
                sql = conn.cursor()
                sql.execute('''
                    INSERT INTO users (full_name, username, email, phone, password, role, due_date, language, linked_mother_username)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session['full_name'],
                    session['username'],
                    session['email'],
                    session['phone'],
                    generate_password_hash(session['password']),
                    session['role'],
                    session['due_date'],
                    session['language'],
                    session['linked_mother_username']
                ))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except Exception as e:
                return f"Error saving to DB: {e}"
        else:
            return "Invalid OTP."
    return render_template("verify_otp.html")

<<<<<<< HEAD
# ------------ LOGIN WITH ATTEMPTS + RESET EMAIL ------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        try:
            conn = sqlite3.connect("data/usalama.db")
            sql = conn.cursor()

            sql.execute("SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier))
            user = sql.fetchone()

            if not user:
                error = "User not found."
                return render_template("login.html", error=error)

            username = user[2]
            stored_password = user[5]

            sql.execute("SELECT failed_attempts FROM login_attempts WHERE username = ?", (username,))
            attempt_data = sql.fetchone()

            if not attempt_data:
                sql.execute("INSERT INTO login_attempts (username, failed_attempts, last_attempt) VALUES (?, 0, ?)", (username, datetime.now()))
                conn.commit()
                failed_attempts = 0
            else:
                failed_attempts = attempt_data[0]

            if failed_attempts >= 3:
                send_reset_email(user[3])  # user[3] = email
                conn.close()
                error = "Too many failed attempts. A password reset email has been sent."
                return render_template("login.html", error=error)

            if check_password_hash(stored_password, password):
                sql.execute("UPDATE login_attempts SET failed_attempts = 0, last_attempt = ? WHERE username = ?", (datetime.now(), username))
                conn.commit()
                session['username'] = username
                role = user[6]
                conn.close()

                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif role == 'mother':
                    return "Mother dashboard (coming soon)"
                elif role == 'partner':
                    return redirect(url_for('partner_dashboard'))
                else:
                    return "Unknown role."
            else:
                sql.execute("UPDATE login_attempts SET failed_attempts = failed_attempts + 1, last_attempt = ? WHERE username = ?", (datetime.now(), username))
                conn.commit()

                sql.execute("SELECT failed_attempts FROM login_attempts WHERE username = ?", (username,))
                attempts = sql.fetchone()[0]

                if attempts >= 3:
                    send_reset_email(user[3])
                    error = "Too many failed attempts. Password reset email sent."
                else:
                    error = f"Invalid credentials. Attempt {attempts}/3"

        except Exception as e:
            error = f"Login error: {e}"
        finally:
            conn.close()

    return render_template("login.html", error=error)

# ------------ RESET EMAIL FUNCTION ------------
def send_reset_email(email):
    token = str(uuid.uuid4())
    created_at = datetime.now()

    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute("""
        INSERT INTO password_resets (email, token, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET token = excluded.token, created_at = excluded.created_at
    """, (email, token, created_at))
    conn.commit()
    conn.close()

    reset_url = url_for('reset_password', token=token, _external=True)
    subject = "Usalama Password Reset"
    body = f"Click to reset your password:\n{reset_url}\nIf you didn’t request this, ignore it."

    sender = 'mpofuemmanuellah@gmail.com'
    app_password = 'fvwm rifq nquu nunk'
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = email
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)
        print("Reset email sent.")
    except Exception as e:
        print("Failed to send reset email:", e)

# ------------ RESET PASSWORD ROUTE ------------
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    error = None
    success = None
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute("SELECT email, created_at FROM password_resets WHERE token = ?", (token,))
    data = sql.fetchone()

    if not data:
        conn.close()
        return render_template("reset_password.html", error="Invalid or expired token.")

    email, created_at_str = data
    created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S.%f")

    if datetime.now() > created_at + timedelta(minutes=15):
        sql.execute("DELETE FROM password_resets WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return render_template("reset_password.html", error="Token expired.")

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password != confirm_password:
            error = "Passwords do not match."
        else:
            hashed_password = generate_password_hash(new_password)
            sql.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
            sql.execute("DELETE FROM password_resets WHERE email = ?", (email,))
            sql.execute("DELETE FROM login_attempts WHERE username = (SELECT username FROM users WHERE email = ?)", (email,))
            conn.commit()
            success = "Password reset successfully. You may now log in."
    conn.close()
    return render_template("reset_password.html", error=error, success=success)

# ------------ REQUEST RESET ROUTE ------------
@app.route('/request-reset', methods=['GET', 'POST'])
def request_reset():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect("data/usalama.db")
        sql = conn.cursor()
        sql.execute("SELECT * FROM users WHERE email = ?", (email,))

# ------------ LOGIN + ADMIN DASHBOARD ROUTE ------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        identifier = request.form['identifier']  # Can be username or email
        password = request.form['password']

        conn = sqlite3.connect("data/usalama.db")
        sql = conn.cursor()
        sql.execute("SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?", 
                    (identifier, identifier, password))

        user = sql.fetchone()
        conn.close()

        if user:
            send_reset_email(email)
            return "Reset link sent to your email."
        else:
            error = "Email not found."
        return render_template("request_reset.html", error=error)

# ------------ DASHBOARD + ADMIN ROUTES ------------
@app.route('/admindashboard')
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("admin_dashboard.html", username=session['username'])

@app.route('/admin/users')
def admin_users():
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute("SELECT id, full_name, username, email, phone, role FROM users")
    users = sql.fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/add_tip', methods=['GET', 'POST'])
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
    return render_template('add_tip.html')

@app.route('/admin/view_tips')
def view_tips():
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute('SELECT id, tip_type, week_number, keyword, language, content FROM text_tips')
    tips = sql.fetchall()
    conn.close()
    return render_template("view_tips.html", tips=tips)

# ------------ ADMIN: VIEW AUDIO TIPS ------------
@app.route('/admin/view_audio')
def view_audio():
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute('SELECT id, tip_type, week_number, keyword, language, file_path FROM audio_tips')
    audio_tips = sql.fetchall()
    conn.close()
    return render_template("view_audio.html", audio_tips=audio_tips)

# ------------ ADMIN: UPLOAD AUDIO TIPS ------------
@app.route('/admin/upload_audio', methods=['GET', 'POST'])
def upload_audio():
    if request.method == 'POST':
        tip_type = request.form['tip_type']
        week_number = request.form.get('week_number')
        keyword = request.form.get('keyword')
        language = request.form['language']
        audio_file = request.files['audio_file']

        if audio_file and allowed_file(audio_file.filename):
            filename = secure_filename(audio_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(save_path)

            conn = sqlite3.connect("data/usalama.db")
            sql = conn.cursor()
            sql.execute('''
                INSERT INTO audio_tips (tip_type, week_number, keyword, language, file_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (tip_type, week_number, keyword, language, filename))
            conn.commit()
            conn.close()
            return render_template("success.html", message="Audio uploaded successfully.")
        return "Invalid file format. Please upload .mp3 or .wav only."
    return render_template("upload_audio.html")

# ------------ AUDIO PLAYBACK ROUTE ------------
@app.route('/audios/<filename>')
def get_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------ ADMIN REPORTS ROUTE ------------
@app.route('/admin/reports')
def admin_reports():
    conn = sqlite3.connect("data/usalama.db")
    cursor = conn.cursor()

    # 1. User Summary by Role
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    user_summary = cursor.fetchall()

    # 2. Login Activity (Failed Attempts)
    cursor.execute("SELECT username, failed_attempts FROM login_attempts ORDER BY failed_attempts DESC")
    login_activity = cursor.fetchall()

    conn.close()

    return render_template("admin_reports.html", user_summary=user_summary, login_activity=login_activity)


# ------------  ADMIN LOGOUT ROUTE ------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------ PARTNER DASHBOARD ROUTE ------------
@app.route('/partnerdashboard')
def partner_dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()

    # Get partner's linked mother
    sql.execute("SELECT linked_mother_username FROM users WHERE username = ?", (username,))
    row = sql.fetchone()
    linked_mother = row[0] if row else None

    mother_info = None
    tips = []

    if linked_mother:
        # Get mother's details
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
                        # Get tips for the calculated week
                        sql.execute("""
                            SELECT tip_type, content FROM text_tips 
                            WHERE week_number = ? AND language = ?
                        """, (pregnancy_weeks, language))
                        tips = sql.fetchall()

                except Exception as e:
                    print("Date parsing error:", e)

    conn.close()

    return render_template("partner_dashboard.html", linked_mother=linked_mother, mother_info=mother_info, tips=tips)
#--------------- CONTACT ROUTE ------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # code to save the contact message to the database or send an email
        print(f"Contact form submitted by {name} ({email}): {message}")
        return render_template("success.html", message="Thank you for contacting us!")

    return render_template("contact.html")
#-------------- FAQ ROUTE ------------
@app.route('/faq')
def faq():
    return render_template("faq.html")

# ------------ ABOUT USALAMA ROUTE ------------
@app.route('/about')
def about():
    return render_template("about.html")

# ------------ HOME PAGE ROUTE ------------
@app.route('/')
def index():
    return render_template('index.html')

#-------------- CSS FILES ROUTE ------------
@app.route('/utilities/css/<path:filename>')
def custom_css(filename):
    return send_from_directory('utilities/css', filename)


# ------------ RUN APP ------------
if __name__ == "__main__":
    app.run(debug=True)
