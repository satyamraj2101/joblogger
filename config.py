# config.py
DATABASE_URI = f"mysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}"
