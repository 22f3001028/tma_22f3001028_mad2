from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models.trek import Trek
from models.booking import Booking
from models.user import User
from utils.decorators import role_required

staff_bp = Blueprint('staff', __name__)


# ============================================================
# STAFF DASHBOARD STATS
# GET /api/staff/dashboard
# ============================================================
@staff_bp.route('/dashboard', methods=['GET'])
@role_required('staff')
def get_dashboard():
    staff_id = int(get_jwt_identity())

    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=staff_id
    ).all()

    trek_ids = [t.id for t in assigned_treks]

    total_participants = Booking.query.filter(
        Booking.trek_id.in_(trek_ids),
        Booking.status == 'Booked'
    ).count() if trek_ids else 0

    ongoing_treks = Trek.query.filter_by(
        assigned_staff_id=staff_id, status='Open'
    ).count()

    return jsonify({
        'assigned_treks': len(assigned_treks),
        'total_participants': total_participants,
        'ongoing_treks': ongoing_treks,
        'treks': [t.to_dict() for t in assigned_treks]
    }), 200


# ============================================================
# VIEW ASSIGNED TREKS
# GET /api/staff/treks
# ============================================================
@staff_bp.route('/treks', methods=['GET'])
@role_required('staff')
def get_assigned_treks():
    staff_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    return jsonify([t.to_dict() for t in treks]), 200


# ============================================================
# VIEW SINGLE TREK + PARTICIPANTS
# GET /api/staff/treks/<id>
# ============================================================
@staff_bp.route('/treks/<int:trek_id>', methods=['GET'])
@role_required('staff')
def get_trek_detail(trek_id):
    staff_id = int(get_jwt_identity())

    trek = Trek.query.filter_by(
        id=trek_id, assigned_staff_id=staff_id
    ).first()

    if not trek:
        return jsonify({
            'error': 'Trek not found or not assigned to you.'
        }), 404

    participants = Booking.query.filter_by(trek_id=trek_id).all()

    return jsonify({
        'trek': trek.to_dict(),
        'participants': [b.to_dict() for b in participants]
    }), 200


# ============================================================
# UPDATE ASSIGNED TREK
# PATCH /api/staff/treks/<id>
# Staff can update status and available_slots only
# ============================================================
@staff_bp.route('/treks/<int:trek_id>', methods=['PATCH'])
@role_required('staff')
def update_trek(trek_id):
    staff_id = int(get_jwt_identity())

    # Critical — staff can only manage their own trek
    trek = Trek.query.filter_by(
        id=trek_id, assigned_staff_id=staff_id
    ).first()

    if not trek:
        return jsonify({
            'error': 'Trek not found or not assigned to you.'
        }), 404

    data = request.get_json()

    # Staff can only update these specific fields
    if 'available_slots' in data:
        new_slots = int(data['available_slots'])
        if new_slots < 0:
            return jsonify({'error': 'Available slots cannot be negative'}), 400
        if new_slots > trek.total_slots:
            return jsonify({
                'error': f'Available slots cannot exceed total slots ({trek.total_slots})'
            }), 400
        trek.available_slots = new_slots

    if 'status' in data:
        allowed = ['Open', 'Closed', 'Completed']
        if data['status'] not in allowed:
            return jsonify({'error': f'Status must be one of: {", ".join(allowed)}'}), 400
        trek.status = data['status']

        # When a trek is marked Completed, mark all active bookings as Completed
        if data['status'] == 'Completed':
            Booking.query.filter_by(
                trek_id=trek_id, status='Booked'
            ).update({'status': 'Completed'})

    db.session.commit()

    return jsonify({
        'message': 'Trek updated successfully.',
        'trek': trek.to_dict()
    }), 200