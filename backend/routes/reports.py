from flask import Blueprint, jsonify
from models.trek import Trek
from models.booking import Booking
from models.user import User
from utils.decorators import role_required
from extensions import db
from datetime import datetime

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/summary', methods=['GET'])
@role_required('admin')
def get_summary():
    now = datetime.utcnow()
    current_month = now.month
    current_year = now.year

    completed_treks = Trek.query.filter_by(status='Completed').all()

    monthly_bookings = Booking.query.filter(
        db.extract('month', Booking.booking_date) == current_month,
        db.extract('year', Booking.booking_date) == current_year
    ).count()

    from sqlalchemy import func
    popular = db.session.query(
        Trek.trek_name,
        func.count(Booking.id).label('booking_count')
    ).join(Booking).group_by(Trek.id).order_by(
        func.count(Booking.id).desc()
    ).limit(5).all()

    return jsonify({
        'month': now.strftime('%B %Y'),
        'completed_treks_total': len(completed_treks),
        'monthly_bookings': monthly_bookings,
        'popular_treks': [
            {'trek_name': name, 'bookings': count}
            for name, count in popular
        ],
        'total_users': User.query.filter_by(role='user').count(),
        'total_staff': User.query.filter_by(role='staff').count(),
        'total_treks': Trek.query.count(),
        'open_treks': Trek.query.filter_by(status='Open').count(),
    }), 200


@reports_bp.route('/send-monthly', methods=['POST'])
@role_required('admin')
def trigger_monthly_report():
    """
    Manually trigger the monthly report email.
    Admin can click a button in the UI to send the report immediately
    instead of waiting for the scheduled job on the 1st of the month.
    """
    try:
        from celery_app import celery
        celery.send_task('tasks.reports.send_monthly_report')
        return jsonify({
            'message': 'Monthly report is being generated and will be emailed to the admin shortly.'
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to trigger report: {str(e)}'
        }), 500