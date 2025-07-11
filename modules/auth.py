# Usalama/modules/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


# ------------------- CONFIG -------------------
SENDER_EMAIL = 'mpofuemmanuellah@gmail.com'
APP_PASSWORD = 'fvwm rifq nquu nunk'

# ------------------- HELPER FUNCTIONS -------------------
def send_otp(email):
    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['email'] = email

    subject = "Usalama OTP Verification"
    body = f"Your Usalama verification code is: {otp}"

    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False

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

    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = "Usalama Password Reset"
    body = f"Click the link to reset your password:\n{reset_url}\nIf you didn’t request this, ignore this message."

    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        print("Reset email sent.")
    except Exception as e:
        print("Failed to send reset email:", e)


# ------------------- ROUTES -------------------

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['full_name'] = request.form['full_name']
        session['username'] = request.form['username']
        session['email'] = request.form['email']
        session['phone'] = request.form['phone']
        session['password'] = request.form['password']
        session['role'] = request.form['role']
        session['due_date'] = request.form.get('due_date')
        session['language'] = request.form['language']
        session['linked_mother_username'] = request.form.get('linked_mother_username')

        if send_otp(session['email']):
            return redirect(url_for('auth.verify_otp'))
        else:
            return "Failed to send OTP. Try again."
    return render_template("register.html")


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
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
                return redirect(url_for('auth.login'))
            except Exception as e:
                return f"Error saving to DB: {e}"
        else:
            return "Invalid OTP."
    return render_template("verify_otp.html")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
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
            send_reset_email(user[3])
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
                return redirect(url_for('admin.admin_dashboard'))
            elif role == 'mother':
                return redirect(url_for('mother.index'))
            elif role == 'partner':
                return redirect(url_for('partner.partner_dashboard'))
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
        conn.close()
    return render_template("login.html", error=error)


@auth_bp.route('/request-reset', methods=['GET', 'POST'])
def request_reset():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect("data/usalama.db")
        sql = conn.cursor()
        sql.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = sql.fetchone()
        conn.close()
        if user:
            send_reset_email(email)
            return "A reset link has been sent to your email."
        else:
            error = "Email not found."
    return render_template("request_reset.html", error=error)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
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


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
