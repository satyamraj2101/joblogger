# dashboard_backend.py
from flask import render_template
from flask_login import login_required, current_user
from flask_mysqldb import MySQL
from app import app  # Assuming 'app' is the Flask application instance
import pymysql

# Initialize MySQL
mysql = MySQL(app)

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Fetch data from the database for the logged-in user
        cur = mysql.connection.cursor(pymysql.cursors.DictCursor)  # Use DictCursor from pymysql

        # Count jobs for each stage
        stages = ['wishlist', 'applied', 'interviewing', 'offer', 'rejected']
        counts = {}

        for stage in stages:
            cur.execute("SELECT COUNT(*) FROM jobs WHERE stage=%s AND user_id=%s", (stage, current_user.id))
            count_result = cur.fetchone()
            counts[stage + '_count'] = count_result['COUNT(*)']

        # Convert the result to a dictionary
        data = {
            'username': current_user.username,
            'wishlist_count': counts['wishlist_count'],
            'applied_count': counts['applied_count'],
            'interviewing_count': counts['interviewing_count'],
            'offer_count': counts['offer_count'],
            'rejected_count': counts['rejected_count']
        }

        return render_template('dashboard.html', **data)

    except Exception as e:
        app.logger.error("Error fetching data from the database: %s", e)
        # Handle the error, e.g., render an error template or redirect to an error page

    finally:
        cur.close()

if __name__ == '__main__':
    app.run(debug=True)
