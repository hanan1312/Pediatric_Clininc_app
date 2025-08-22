# create_db.py
from src.models.user import db
from src.models.patient import Patient # Import your Patient model
from flask import Flask
import os

# Assuming your Flask app setup is similar to this
# You might need to adjust the import for 'db' and 'Patient' based on your actual project structure
# For example, if 'db' is initialized within your main app.py, you might need to import app.
# If db is a standalone SQLAlchemy instance, this should work.

# Basic Flask app setup for context (adjust if your setup is different)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with the app
db.init_app(app)

def create_database():
    """Creates a new SQLite database with all defined models."""
    with app.app_context():
        # Ensure the directory for app.db exists if it's not in the root
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created directory: {db_dir}")

        # Drop all existing tables (if any) and then create them based on models
        # WARNING: This will delete all data in your database!
        db.drop_all()
        db.create_all()
        print("Database 'app.db' created/recreated successfully with all tables.")

if __name__ == '__main__':
    create_database()
