from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mysqldb import MySQL
from wtforms import SelectField, DateField, TextAreaField
import os
import logging
from datetime import date

app = Flask(__name__, template_folder='template')
app.config.from_pyfile('config.py')

# Initialize MySQL
mysql = MySQL(app)

# Set up logging to a file
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs.txt')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Flask-Login configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = app.config['SECRET_KEY'] or os.urandom(24)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

# SQL command to create the jobs table
CREATE_JOBS_TABLE = """
    CREATE TABLE IF NOT EXISTS jobs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company_name VARCHAR(255) NOT NULL,
        position VARCHAR(255) NOT NULL,
        stage VARCHAR(255) NOT NULL,
        salary VARCHAR(255),
        job_type VARCHAR(255),
        url VARCHAR(255),
        applied_on DATE,
        description TEXT,
        location VARCHAR(255),
        application_type VARCHAR(255) NOT NULL,
        user_id INT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
"""

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

# Flask-WTF form for the add_job route
class AddJobForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    stage = SelectField('Stage', choices=[
        ('wishlist', 'Wishlist'),
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected')],
        validators=[DataRequired()])
    salary = StringField('Salary')
    job_type = SelectField('Job Type', choices=[
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('onsite', 'Onsite')])
    url = StringField('URL')
    applied_on = DateField('Applied On', format='%Y-%m-%d')
    description = TextAreaField('Description Box')
    location = StringField('Location')
    application_type = SelectField('Application Type', choices=[
        ('part-time', 'Part-time'),
        ('full-time', 'Full-time'),
        ('internship', 'Internship')],
        validators=[DataRequired()])

@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    form = AddJobForm()

    if form.validate_on_submit():
        # Retrieve form data
        app.logger.info("Form Data: %s", form.data)  # Log form data for debugging

        company_name = form.company_name.data
        position = form.position.data
        stage = form.stage.data
        salary = form.salary.data
        job_type = form.job_type.data
        url = form.url.data
        applied_on = form.applied_on.data.strftime('%Y-%m-%d') if form.applied_on.data else None
        description = form.description.data
        location = form.location.data
        application_type = form.application_type.data

        # Save the form data to the database
        cur = mysql.connection.cursor()

        try:
            # Create the jobs table if it doesn't exist
            cur.execute(CREATE_JOBS_TABLE)

            # Insert job data for the current user
            cur.execute("""
                INSERT INTO jobs 
                    (company_name, position, stage, salary, job_type, url, applied_on, description, location, application_type, user_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                company_name, position, stage, salary, job_type, url, applied_on, description, location, application_type,
                current_user.id))

            mysql.connection.commit()
            flash('Job added successfully!', 'success')

            # Redirect to the 'dashboard' route after successfully adding the job
            return redirect(url_for('dashboard'))

        except Exception as e:
            app.logger.error("Error Saving Data: %s", e)  # Log statement for debugging
            flash('Error saving job data. Please check the logs for details.', 'danger')

        finally:
            cur.close()

    # Render the 'add_job.html' template if the form is not valid or an exception occurred
    return render_template('add_job.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
