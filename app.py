from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# License model for the database
class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_key = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)

# Create the database tables within the application context
with app.app_context():
    db.create_all()

# Sample function to add a new license (for testing)
def add_sample_license():
    if not License.query.filter_by(license_key="sample_key_123").first():
        new_license = License(
            license_key="sample_key_123",
            status="valid",
            expiration_date=datetime.datetime(2025, 12, 31)
        )
        db.session.add(new_license)
        db.session.commit()

# Add a sample license when the app starts (for testing purposes)
with app.app_context():
    add_sample_license()

# Home route
@app.route('/')
def home():
    return "License Management and Validation System for Software as a Service (SAAS).This system is designed to ensure secure and centralized license validation !"


# API endpoint to validate licenses
@app.route('/validate', methods=['POST'])
def validate_license():
    data = request.json
    license_key = data.get("license_key")
    license_record = License.query.filter_by(license_key=license_key).first()

    if license_record:
        # Check if the license is still valid
        if license_record.expiration_date > datetime.datetime.now():
            return jsonify({"status": "valid", "expiration_date": license_record.expiration_date.strftime('%Y-%m-%d')}), 200
        else:
            return jsonify({"status": "expired"}), 403
    return jsonify({"status": "invalid"}), 403


# Flask-Admin interface to manage licenses

admin = Admin(app, name='License Management', template_mode='bootstrap3')
admin.add_view(ModelView(License, db.session))

if __name__ == '__main__':
    app.run(debug=True)
