from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mysqldb import MySQL
import os

app = Flask(__name__, template_folder='template')
app.config.from_pyfile('config.py')

# Initialize MySQL
mysql = MySQL(app)

# Flask-Login configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = app.config['SECRET_KEY'] or os.urandom(24)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

# Flask-WTF forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user_data = cur.fetchone()
    cur.close()

    if user_data:
        return User(user_data[0], user_data[1])  # Assuming 'id' is the first element and 'username' is the second
    return None

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch data from the database for the logged-in user
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT username, wishlist_count, applied_count, interviewing_count, offer_count, rejected_count
        FROM application_status
        WHERE username = %s
    """, (current_user.username,))
    status_data = cur.fetchone()
    cur.close()

    if status_data:
        # Convert the result to a dictionary
        data = {
            'username': status_data[0],
            'wishlist_count': status_data[1],
            'applied_count': status_data[2],
            'interviewing_count': status_data[3],
            'offer_count': status_data[4],
            'rejected_count': status_data[5]
        }
    else:
        # Default values if no data is found
        data = {
            'username': current_user.username,
            'wishlist_count': 0,
            'applied_count': 0,
            'interviewing_count': 0,
            'offer_count': 0,
            'rejected_count': 0
        }

    return render_template('dashboard.html', **data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Authenticate user using MySQL
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user_data = cur.fetchone()
        cur.close()

        if user_data:
            user = User(user_data[0], user_data[1])  # Assuming 'id' is the first element and 'username' is the second
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if the username is already in use
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            flash('Username already in use. Please choose a different one.', 'danger')
        else:
            # Insert the new user into the database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            mysql.connection.commit()
            cur.close()

            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        # Implement your logic to handle the password reset (send email, generate token, etc.)
        flash(f"Password reset requested for email: {email}. (Not implemented in this example)", 'info')

    return render_template('forgot_password.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
