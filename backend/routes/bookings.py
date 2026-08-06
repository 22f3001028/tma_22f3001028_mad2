from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models.booking import Booking
from models.trek import Trek
from utils.decorators import role_required

bookings_bp = Blueprint('bookings', __name__)


# ============================================================
# CREATE BOOKING
# POST /api/bookings
# ============================================================
@bookings_bp.route('', methods=['POST'])
@role_required('user')
def create_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('trek_id'):
        return jsonify({'error': 'trek_id is required'}), 400

    trek = Trek.query.get(data['trek_id'])
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    # Business rule 1 — only open treks can be booked
    if trek.status != 'Open':
        return jsonify({
            'error': f'This trek is currently {trek.status} and cannot be booked.'
        }), 400

    # Business rule 2 — no overbooking
    if trek.available_slots <= 0:
        return jsonify({'error': 'Sorry, this trek is fully booked.'}), 400

    # Business rule 3 — no duplicate booking
    existing = Booking.query.filter_by(
        user_id=user_id,
        trek_id=trek.id,
        status='Booked'
    ).first()
    if existing:
        return jsonify({'error': 'You have already booked this trek.'}), 409

    # Create the booking and reduce available slots
    booking = Booking(
        user_id=user_id,
        trek_id=trek.id,
        status='Booked'
    )
    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()

    return jsonify({
        'message': f'You have successfully booked {trek.trek_name}!',
        'booking': booking.to_dict()
    }), 201


# ============================================================
# VIEW MY BOOKINGS
# GET /api/bookings/me
# ============================================================
@bookings_bp.route('/me', methods=['GET'])
@role_required('user')
def get_my_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(
        user_id=user_id
    ).order_by(Booking.booking_date.desc()).all()

    return jsonify([b.to_dict() for b in bookings]), 200


# ============================================================
# CANCEL BOOKING
# DELETE /api/bookings/<id>
# ============================================================
@bookings_bp.route('/<int:booking_id>', methods=['DELETE'])
@role_required('user')
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())

    booking = Booking.query.filter_by(
        id=booking_id, user_id=user_id
    ).first()

    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.status != 'Booked':
        return jsonify({
            'error': f'Cannot cancel a booking that is already {booking.status}.'
        }), 400

    # Restore the slot when booking is cancelled
    booking.status = 'Cancelled'
    booking.trek.available_slots += 1

    db.session.commit()

    return jsonify({
        'message': 'Your booking has been cancelled and your slot has been released.'
    }), 200