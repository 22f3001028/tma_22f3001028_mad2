from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(10), nullable=False, default='user')
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """
        Hash the plain-text password and store the hash.
        The original password is never stored.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check whether the provided password matches
        the stored password hash.
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """
        Convert the User object into a dictionary
        that can safely be returned by an API.
        """
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'contact_number': self.contact_number,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }