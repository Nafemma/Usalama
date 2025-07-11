# app.py

from flask import Flask, send_from_directory, render_template
import os

# ------------ APP SETUP ------------
app = Flask(__name__)
app.secret_key = "usalama_secret"

# ------------ AUDIO CONFIG ------------
UPLOAD_FOLDER = 'audios'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------ BLUEPRINT IMPORTS ------------
from modules.auth import auth_bp
from modules.admin import admin_bp
from modules.mother import mother_bp
from modules.partner import partner_bp

# ------------ REGISTER BLUEPRINTS ------------
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(mother_bp)
app.register_blueprint(partner_bp)

# ------------ STATIC + PUBLIC ROUTES ------------
@app.route('/audios/<filename>')
def get_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/utilities/css/<path:filename>')
def custom_css(filename):
    return send_from_directory('utilities/css', filename)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    from flask import request
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        print(f"Contact message from {name}: {message}")
        return render_template("success.html", message="Thank you for contacting us!")
    return render_template("contact.html")

@app.route('/logout')
def logout():
    from flask import session, redirect, url_for
    session.clear()
    return redirect(url_for('auth.login'))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/utilities/imgs/<path:filename>')
def custom_img(filename):
    return send_from_directory('utilities/imgs', filename)


# ------------ RUN APP ------------
if __name__ == "__main__":
    app.run(debug=True)
