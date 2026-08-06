from extensions import db
from datetime import datetime


class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)

    trek_name = db.Column(db.String(150), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    duration_days = db.Column(db.Integer, nullable=False)

    start_date = db.Column(db.Date, nullable=False)

    end_date = db.Column(db.Date, nullable=False)

    total_slots = db.Column(db.Integer, nullable=False)

    available_slots = db.Column(db.Integer, nullable=False)

    status = db.Column(
        db.String(20),
        nullable=False,
        default='Pending'
    )

    description = db.Column(db.Text, nullable=True)

    instructions = db.Column(db.Text, nullable=True)

    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    assigned_staff = db.relationship(
        'User',
        backref='assigned_treks',
        foreign_keys=[assigned_staff_id]
    )

    def to_dict(self):
        return {
            'id': self.id,
            'trek_name': self.trek_name,
            'location': self.location,
            'difficulty': self.difficulty,
            'duration_days': self.duration_days,
            'start_date': self.start_date.isoformat()
                if self.start_date else None,
            'end_date': self.end_date.isoformat()
                if self.end_date else None,
            'total_slots': self.total_slots,
            'available_slots': self.available_slots,
            'status': self.status,
            'description': self.description,
            'instructions': self.instructions,
            'assigned_staff_id': self.assigned_staff_id,
            'assigned_staff_name': (
                self.assigned_staff.full_name
                if self.assigned_staff else None
            ),
            'created_at': self.created_at.isoformat()
                if self.created_at else None
        }