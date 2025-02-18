from flask import Blueprint, render_template, flash, redirect, url_for, request, g, current_app, Response
from app import db
from app.forms import LoginForm, RegistrationForm, EmptyForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from app.register_face import register_face
from urllib.parse import urlparse
from datetime import datetime
from flask_babel import _, get_locale
import face_recognition
import cv2
from werkzeug.utils import secure_filename
import numpy as np
import io
from PIL import Image
import os


bp = Blueprint('main', __name__)

FACE_REG_DIR = "faces/"

if not os.path.exists(FACE_REG_DIR):
    os.makedirs(FACE_REG_DIR)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')
from app.forms import LoginForm

# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     # Ensure login page only allows login attempts if the user is not logged in
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))  # If logged in, send to index

#     form = LoginForm()

#     # Handle login logic with face recognition
#     if request.method == 'POST' and form.validate_on_submit():
#         # Capture a photo for authentication
#         cap = cv2.VideoCapture(0)
#         ret, frame = cap.read()
#         cap.release()

#         if not ret:
#             flash("Error capturing image. Try again.")
#             return redirect(url_for('main.login'))

#         # Encode the captured face
#         captured_encoding = face_recognition.face_encodings(frame)
#         if not captured_encoding:
#             flash("No face detected. Try again.")
#             return redirect(url_for('main.login'))

#         captured_encoding = captured_encoding[0]

#         # Compare with stored face encodings
#         for filename in os.listdir(FACE_REG_DIR):
#             stored_image_path = os.path.join(FACE_REG_DIR, filename)
#             stored_image = face_recognition.load_image_file(stored_image_path)
#             stored_encoding = face_recognition.face_encodings(stored_image)

#             if stored_encoding:
#                 stored_encoding = stored_encoding[0]
#                 match = face_recognition.compare_faces([stored_encoding], captured_encoding, tolerance=0.5)

#                 if match[0]:
#                     username = filename.split(".")[0]
#                     user = User.query.filter_by(username=username).first()
#                     if user:
#                         login_user(user)
#                         flash(f"Welcome back, {username}!")
#                         return redirect(url_for('main.index'))  # Successful login

#         flash("Face not recognized. Try again or register.")
#         return redirect(url_for('main.login'))  # Re-try login if face not recognized

#     # Render login page if GET request
#     return render_template('login.html', form=form)  # Pass the form to the template

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  

    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data.strip()

        # Check if the username exists
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Username not found. Please register first.")
            return redirect(url_for('main.login'))

        # Capture a photo for authentication
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            flash("Error capturing image. Try again.")
            return redirect(url_for('main.login'))

        # Encode the captured face
        captured_encoding = face_recognition.face_encodings(frame)
        if not captured_encoding:
            flash("No face detected. Try again.")
            return redirect(url_for('main.login'))

        captured_encoding = captured_encoding[0]

        # Compare with stored face encoding of the provided username
        user_face_path = os.path.join(FACE_REG_DIR, f"{username}.jpg")
        if not os.path.exists(user_face_path):
            flash("Face not registered. Please register first.")
            return redirect(url_for('main.login'))

        stored_image = face_recognition.load_image_file(user_face_path)
        stored_encoding = face_recognition.face_encodings(stored_image)

        if stored_encoding:
            stored_encoding = stored_encoding[0]
            match = face_recognition.compare_faces([stored_encoding], captured_encoding, tolerance=0.5)

            if match[0]:  # If face matches the username
                login_user(user)
                flash(f"Welcome back, {username}!")
                return redirect(url_for('main.index'))

        flash("Face and username do not match. Try again.")
        return redirect(url_for('main.login'))

    return render_template('login.html', form=form)  


@bp.route('/logout')
def logout():
    # Print for debugging session
    print(f"Logging out user: {current_user.username if current_user.is_authenticated else 'No User Logged In'}")
    
    # Logout user
    logout_user()
    flash("You have been logged out.")

    # Explicitly redirect to the login page to make sure session is cleared
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')

        # Check if username is provided
        if not username:
            flash("Please enter a username.")
            return redirect(url_for('main.register'))

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken. Choose a different one.")
            return redirect(url_for('main.register'))

        # Call the function to register the face
        register_face(username)

        # Register user in the database
        user = User(username=username)
        db.session.add(user)
        db.session.commit()

        flash("Face registered successfully! You can now log in.")
        return redirect(url_for('main.login'))

    return render_template('register.html')  # Render registration page

@bp.route('/video_feed')
def video_feed():
    cap = cv2.VideoCapture(0)

    def generate_frames():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')