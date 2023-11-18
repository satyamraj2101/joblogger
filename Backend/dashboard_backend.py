# dashboard_backend.py
from flask import render_template
from flask_login import login_required, current_user
from flask_mysqldb import MySQL
from app import app  # Assuming 'app' is the Flask application instance

# Initialize MySQL
mysql = MySQL(app)

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

if __name__ == '__main__':
    app.run(debug=True)
