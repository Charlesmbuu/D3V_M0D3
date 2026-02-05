from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    """
    Represents system users (both subscribers and ISP staff)
    Inherits from UserMixin for Flask-Login compatibility
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    speed_tests = db.relationship('SpeedTest', backref='user', lazy='dynamic')
    outages = db.relationship('Outage', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Create hashed password using werkzeug security"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify hashed password"""
        return check_password_hash(self.password_hash, password)

class SpeedTest(db.Model):
    """Stores results of network speed tests"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    download = db.Column(db.Float)  # Mbps
    upload = db.Column(db.Float)    # Mbps
    ping = db.Column(db.Float)      # ms
    server_location = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Outage(db.Model):
    """Tracks network outage incidents"""
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Float)  # Minutes
    resolved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)

class NetworkNode(db.Model):
    """Represents physical network infrastructure"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String(20), default='operational')
    last_maintenance = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(id):
    """Required Flask-Login user loader callback"""
    return User.query.get(int(id))