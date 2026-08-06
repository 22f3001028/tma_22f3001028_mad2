from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models.trek import Trek
from models.user import User
from utils.decorators import role_required
from services.cache_service import get_cached, set_cached
from services.export_service import generate_booking_csv
user_bp = Blueprint('user', __name__)


# ============================================================
# BROWSE OPEN TREKS (with search and filter)
# GET /api/user/treks
# ============================================================
@user_bp.route('/treks', methods=['GET'])
@role_required('user')
def browse_treks():
    search = request.args.get('search', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip()

    # Use cache only when no filters are applied
    if not search and not difficulty and not location:
        cached = get_cached('open_treks')
        if cached:
            return jsonify(cached), 200

    query = Trek.query.filter_by(status='Open')

    if search:
        query = query.filter(
            (Trek.trek_name.ilike(f'%{search}%')) |
            (Trek.location.ilike(f'%{search}%'))
        )
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))

    treks = query.order_by(Trek.start_date.asc()).all()
    result = [t.to_dict() for t in treks]

    # Cache the unfiltered result only
    if not search and not difficulty and not location:
        set_cached('open_treks', result)

    return jsonify(result), 200


# ============================================================
# VIEW TREK DETAIL
# GET /api/user/treks/<id>
# ============================================================
@user_bp.route('/treks/<int:trek_id>', methods=['GET'])
@role_required('user')
def get_trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return jsonify(trek.to_dict()), 200


# ============================================================
# VIEW AND UPDATE OWN PROFILE
# GET/PUT /api/user/profile
# ============================================================
@user_bp.route('/profile', methods=['GET'])
@role_required('user')
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route('/profile', methods=['PUT'])
@role_required('user')
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'full_name' in data and data['full_name']:
        user.full_name = data['full_name']
    if 'contact_number' in data:
        user.contact_number = data['contact_number']

    # Password change — only if both fields provided
    if data.get('current_password') and data.get('new_password'):
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        user.set_password(data['new_password'])

    db.session.commit()
    return jsonify({
        'message': 'Profile updated successfully.',
        'user': user.to_dict()
    }), 200

# ============================================================
# EXPORT BOOKING HISTORY AS CSV
# GET /api/user/export/bookings
# ============================================================
@user_bp.route('/export/bookings', methods=['GET'])
@role_required('user')
def export_bookings():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    # Generate CSV content — batch processes all records server-side
    csv_content = generate_booking_csv(user_id)

    safe_name = user.full_name.replace(' ', '_').lower()
    filename = f'booking_history_{safe_name}.csv'

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )