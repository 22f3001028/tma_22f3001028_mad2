from extensions import db
from datetime import datetime


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey('treks.id'),
        nullable=False
    )

    # Status lifecycle: Booked → Cancelled (by user) or Completed (when trek ends)
    status = db.Column(
        db.String(20),
        nullable=False,
        default='Booked'
    )

    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relationships — lets us write booking.user and booking.trek
    user = db.relationship('User', backref='bookings')
    trek = db.relationship('Trek', backref='bookings')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trek_id': self.trek_id,
            'status': self.status,
            'booking_date': self.booking_date.isoformat(),
            # Include related data so frontend doesn't need extra API calls
            'trek_name': self.trek.trek_name if self.trek else None,
            'location': self.trek.location if self.trek else None,
            'difficulty': self.trek.difficulty if self.trek else None,
            'start_date': self.trek.start_date.isoformat() if self.trek and self.trek.start_date else None,
            'end_date': self.trek.end_date.isoformat() if self.trek and self.trek.end_date else None,
            'trek_status': self.trek.status if self.trek else None,
            'user_name': self.user.full_name if self.user else None,
            'user_email': self.user.email if self.user else None,
        }