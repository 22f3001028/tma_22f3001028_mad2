from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models.user import User
from models.trek import Trek
from models.booking import Booking
from utils.decorators import role_required
from services.cache_service import invalidate_trek_caches

admin_bp = Blueprint('admin', __name__)


# ============================================================
# DASHBOARD STATS
# GET /api/admin/dashboard
# ============================================================
@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def get_dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()

    recent_bookings = Booking.query.order_by(
        Booking.booking_date.desc()
    ).limit(5).all()

    return jsonify({
        'total_treks': total_treks,
        'total_users': total_users,
        'total_staff': total_staff,
        'total_bookings': total_bookings,
        'recent_bookings': [b.to_dict() for b in recent_bookings]
    }), 200


# ============================================================
# TREK MANAGEMENT
# ============================================================

@admin_bp.route('/treks', methods=['GET'])
@role_required('admin')
def get_all_treks():
    treks = Trek.query.order_by(Trek.created_at.desc()).all()
    return jsonify([t.to_dict() for t in treks]), 200


@admin_bp.route('/treks', methods=['POST'])
@role_required('admin')
def create_trek():
    data = request.get_json()

    required = ['trek_name', 'location', 'difficulty',
                'duration_days', 'start_date', 'end_date',
                'total_slots']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # Validate difficulty value
    if data['difficulty'] not in ['Easy', 'Moderate', 'Hard']:
        return jsonify({'error': 'Difficulty must be Easy, Moderate, or Hard'}), 400

    # Validate slot count
    if int(data['total_slots']) <= 0:
        return jsonify({'error': 'Total slots must be greater than 0'}), 400

    from datetime import date
    try:
        start = date.fromisoformat(data['start_date'])
        end = date.fromisoformat(data['end_date'])
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if end <= start:
        return jsonify({'error': 'End date must be after start date'}), 400

    trek = Trek(
        trek_name=data['trek_name'],
        location=data['location'],
        difficulty=data['difficulty'],
        duration_days=int(data['duration_days']),
        start_date=start,
        end_date=end,
        total_slots=int(data['total_slots']),
        available_slots=int(data['total_slots']),  # starts equal to total
        status='Pending',
        description=data.get('description'),
        instructions=data.get('instructions'),
        assigned_staff_id=data.get('assigned_staff_id')
    )

    db.session.add(trek)
    db.session.commit()
    invalidate_trek_caches()

    return jsonify({
        'message': 'Trek created successfully.',
        'trek': trek.to_dict()
    }), 201


@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@role_required('admin')
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()

    # Update only fields that are provided
    if 'trek_name' in data:
        trek.trek_name = data['trek_name']
    if 'location' in data:
        trek.location = data['location']
    if 'difficulty' in data:
        if data['difficulty'] not in ['Easy', 'Moderate', 'Hard']:
            return jsonify({'error': 'Difficulty must be Easy, Moderate, or Hard'}), 400
        trek.difficulty = data['difficulty']
    if 'duration_days' in data:
        trek.duration_days = int(data['duration_days'])
    if 'description' in data:
        trek.description = data['description']
    if 'instructions' in data:
        trek.instructions = data['instructions']
    if 'status' in data:
        if data['status'] not in ['Pending', 'Open', 'Closed', 'Completed']:
            return jsonify({'error': 'Invalid status value'}), 400
        trek.status = data['status']
    if 'assigned_staff_id' in data:
        # Verify the staff member exists and has the right role
        if data['assigned_staff_id']:
            staff = User.query.filter_by(
                id=data['assigned_staff_id'], role='staff'
            ).first()
            if not staff:
                return jsonify({'error': 'Staff member not found'}), 404
        trek.assigned_staff_id = data['assigned_staff_id']

    db.session.commit()
    invalidate_trek_caches()

    return jsonify({
        'message': 'Trek updated successfully.',
        'trek': trek.to_dict()
    }), 200


@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@role_required('admin')
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    # Prevent deletion if there are active bookings
    active_bookings = Booking.query.filter_by(
        trek_id=trek_id, status='Booked'
    ).count()
    if active_bookings > 0:
        return jsonify({
            'error': f'Cannot delete trek with {active_bookings} active booking(s).'
        }), 400

    db.session.delete(trek)
    db.session.commit()
    invalidate_trek_caches()

    return jsonify({'message': 'Trek deleted successfully.'}), 200


# ============================================================
# STAFF MANAGEMENT
# ============================================================

@admin_bp.route('/staff', methods=['GET'])
@role_required('admin')
def get_all_staff():
    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='staff')

    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    staff = query.order_by(User.created_at.desc()).all()
    return jsonify([s.to_dict() for s in staff]), 200


@admin_bp.route('/staff', methods=['POST'])
@role_required('admin')
def create_staff():
    data = request.get_json()

    required = ['full_name', 'email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    staff = User(
        full_name=data['full_name'],
        email=data['email'],
        contact_number=data.get('contact_number'),
        role='staff',
        status='active'
    )
    staff.set_password(data['password'])

    db.session.add(staff)
    db.session.commit()

    return jsonify({
        'message': f'Staff account created for {staff.full_name}.',
        'staff': staff.to_dict()
    }), 201


@admin_bp.route('/staff/<int:staff_id>/status', methods=['PATCH'])
@role_required('admin')
def update_staff_status(staff_id):
    staff = User.query.filter_by(id=staff_id, role='staff').first_or_404()
    data = request.get_json()

    if data.get('status') not in ['active', 'blacklisted', 'inactive']:
        return jsonify({'error': 'Invalid status value'}), 400

    staff.status = data['status']
    db.session.commit()

    return jsonify({
        'message': f'Staff status updated to {staff.status}.',
        'staff': staff.to_dict()
    }), 200


# ============================================================
# USER MANAGEMENT
# ============================================================

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='user')

    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    users = query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PATCH'])
@role_required('admin')
def update_user_status(user_id):
    user = User.query.filter_by(id=user_id, role='user').first_or_404()
    data = request.get_json()

    if data.get('status') not in ['active', 'blacklisted', 'inactive']:
        return jsonify({'error': 'Invalid status value'}), 400

    user.status = data['status']
    db.session.commit()

    return jsonify({
        'message': f'User status updated to {user.status}.',
        'user': user.to_dict()
    }), 200