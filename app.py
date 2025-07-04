# ------------ IMPORTS ------------
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3  # For database operations
import random   # For generating OTP
import smtplib  # For sending OTP email
import os       # For file and path operations
from email.message import EmailMessage  # For formatting email messages
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
                    session['password'],
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
            role = user[6]
            session['username'] = user[2]
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return "Access denied. Not an admin."
        else:
            error = "Invalid credentials. Try again."
    return render_template("login.html", error=error)

@app.route('/admindashboard')
def admin_dashboard():
    username = session.get('username', 'Unknown')
    return render_template("admin_dashboard.html", username=username)

# ------------ ADMIN: VIEW USERS ------------
@app.route('/admin/users')
def admin_users():
    conn = sqlite3.connect("data/usalama.db")
    sql = conn.cursor()
    sql.execute("SELECT id, full_name, username, email, phone, role FROM users")
    users = sql.fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

# ------------ ADMIN: ADD TEXT TIP ------------
@app.route('/admin/add_tip', methods=['GET', 'POST'])
def add_tip():
    if request.method == 'POST':
        tip_type = request.form['tip_type']
        week_number = request.form.get('week_number')
        keyword = request.form.get('keyword')
        language = request.form['language']
        content = request.form['content']

        week_number = int(week_number) if week_number else None
        keyword = keyword if keyword else None

        conn = sqlite3.connect("data/usalama.db")
        sql = conn.cursor()
        sql.execute('''
            INSERT INTO text_tips (tip_type, week_number, keyword, language, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (tip_type, week_number, keyword, language, content))
        conn.commit()
        conn.close()
        return render_template("success.html", message=" Health tip uploaded successfully!")

    return render_template('add_tip.html')

# ------------ ADMIN: VIEW TEXT TIPS ------------
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
           # Save the file in the 'audios/' folder
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(save_path)

            week_number = int(week_number) if week_number else None
            keyword = keyword if keyword else None

            conn = sqlite3.connect("data/usalama.db")
            sql = conn.cursor()
            # Save only the filename (e.g., "babycare.mp3") in the database
            sql.execute('''
            INSERT INTO audio_tips (tip_type, week_number, keyword, language, file_path)
            VALUES (?, ?, ?, ?, ?)
            ''', (tip_type, week_number, keyword, language, filename))
            conn.commit()
            conn.close()

            return render_template("success.html", message=" Audio tip uploaded successfully!")

        return " Invalid file format. Please upload .mp3 or .wav only."

    return render_template("upload_audio.html")

# ------------ AUDIO TIP PLAYBACK ROUTE ------------
@app.route('/audios/<filename>')
def get_audio(filename):
    # This makes audio files inside 'audios/' available at /audios/<filename>
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------ MAIN ------------
if __name__ == "__main__":
    app.run(debug=True)
