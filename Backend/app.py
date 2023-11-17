from flask import Flask, render_template
from flask_mysqldb import MySQL
from config import DATABASE_URI

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'sql12.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql12662911'
app.config['MYSQL_PASSWORD'] = 'PSqhR4Tpuz'
app.config['MYSQL_DB'] = 'sql12662911'

# Initialize MySQL
mysql = MySQL(app)

# Create a table if it doesn't exist
with app.app_context():
    cursor = mysql.connection.cursor()

    # Example: Create a 'jobs' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT
        )
    ''')

    # Commit changes
    mysql.connection.commit()

    # Close cursor
    cursor.close()

@app.route('/')
def index():
    # Use MySQL queries here
    cur = mysql.connection.cursor()
    # Example query: cur.execute("SELECT * FROM jobs")
    # result = cur.fetchall()
    # Close the cursor
    cur.close()
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
