from flask import Flask, render_template
import mysql.connector
from config import DATABASE_URI

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'sql12.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql12662911'
app.config['MYSQL_PASSWORD'] = 'PSqhR4Tpuz'
app.config['MYSQL_DB'] = 'sql12662911'

try:
    mysql_connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    print("Connected to the database.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    # Handle the error as needed

@app.route('/')
def index():
    # Use MySQL queries here
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
