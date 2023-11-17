from flask import Flask , render_template, request, flash, redirect, url_for
from models import User
from . import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

app = Flask(__name__,template_folder='template')
app.config['SECRET_KEY'] = 'satyamraj123'  # Change this to a secure secret key

# Mock database for demonstration purposes
users = [{'username': 'user1', 'password': 'password1'}, {'username': 'user2', 'password': 'password2'}]

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Signup')

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check username and password (mock authentication for demonstration)
        username = form.username.data
        password = form.password.data
        if any(user['username'] == username and user['password'] == password for user in users):
            return f'Welcome, {username}!'
        else:
            return 'Invalid username or password'
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  # Add this line to get the email from the form
        password = request.form.get('password')

        # Check if the email is already in use
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address is already in use. Please use a different email.', 'error')
            return redirect(url_for('signup'))

        # Create a new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Send email with password reset link
            # ... (use Flask-Mail or your preferred email service)
            flash('An email with instructions to reset your password has been sent.', 'info')
        else:
            flash('No user found with that email address.', 'error')
    return render_template('forgot_password.html')

if __name__ == '__main__':
    app.run(debug=True)
