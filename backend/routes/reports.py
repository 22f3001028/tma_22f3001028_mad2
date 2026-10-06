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
    Directly generates and sends the monthly report email.
    Runs synchronously - no Celery needed.
    """
    try:
        from models.trek import Trek
        from models.booking import Booking
        from models.user import User
        from extensions import mail, db
        from flask_mail import Message
        from sqlalchemy import func
        from datetime import datetime
        from flask import current_app

        now = datetime.utcnow()
        month_label = now.strftime('%B %Y')
        current_month = now.month
        current_year = now.year

        # Gather stats
        total_treks = Trek.query.count()
        completed_treks = Trek.query.filter_by(status='Completed').count()
        open_treks = Trek.query.filter_by(status='Open').count()
        total_users = User.query.filter_by(role='user').count()

        monthly_bookings = Booking.query.filter(
            db.extract('month', Booking.booking_date) == current_month,
            db.extract('year', Booking.booking_date) == current_year
        ).count()

        popular = db.session.query(
            Trek.trek_name,
            func.count(Booking.id).label('booking_count')
        ).join(Booking).group_by(Trek.id).order_by(
            func.count(Booking.id).desc()
        ).limit(5).all()

        # Build popular treks rows
        popular_rows = ''
        medals = ['🥇', '🥈', '🥉']
        for i, (name, count) in enumerate(popular, 1):
            medal = medals[i-1] if i <= 3 else str(i)
            bg = '#f8f9fa' if i % 2 == 0 else '#ffffff'
            popular_rows += f"""
            <tr style="background-color:{bg}">
                <td style="padding:10px">{medal}</td>
                <td style="padding:10px"><strong>{name}</strong></td>
                <td style="padding:10px;text-align:center">
                    <span style="background:#212529;color:white;
                                 padding:2px 10px;border-radius:12px">
                        {count}
                    </span>
                </td>
            </tr>"""

        if not popular_rows:
            popular_rows = '<tr><td colspan="3" style="padding:20px;text-align:center;color:#6c757d">No bookings this month.</td></tr>'

        html_body = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;">
            <div style="background:#212529;padding:24px;border-radius:8px 8px 0 0;">
                <h1 style="color:white;margin:0;">🏔️ Trekking Management</h1>
                <p style="color:#adb5bd;margin:6px 0 0;">Monthly Activity Report</p>
            </div>
            <div style="padding:30px;background:#ffffff;border:1px solid #dee2e6;">
                <h2>Report for {month_label}</h2>
                <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
                    <tr style="background:#e9ecef;">
                        <td style="padding:12px;font-weight:bold;">Total Treks</td>
                        <td style="padding:12px;font-size:20px;font-weight:bold;">{total_treks}</td>
                    </tr>
                    <tr>
                        <td style="padding:12px;font-weight:bold;">Open Treks</td>
                        <td style="padding:12px;font-size:20px;color:#198754;font-weight:bold;">{open_treks}</td>
                    </tr>
                    <tr style="background:#e9ecef;">
                        <td style="padding:12px;font-weight:bold;">Completed Treks</td>
                        <td style="padding:12px;font-size:20px;color:#0d6efd;font-weight:bold;">{completed_treks}</td>
                    </tr>
                    <tr>
                        <td style="padding:12px;font-weight:bold;">Bookings This Month</td>
                        <td style="padding:12px;font-size:20px;font-weight:bold;">{monthly_bookings}</td>
                    </tr>
                    <tr style="background:#e9ecef;">
                        <td style="padding:12px;font-weight:bold;">Registered Trekkers</td>
                        <td style="padding:12px;font-size:20px;font-weight:bold;">{total_users}</td>
                    </tr>
                </table>
                <h3 style="border-bottom:2px solid #dee2e6;padding-bottom:8px;">🔥 Popular Treks</h3>
                <table style="width:100%;border-collapse:collapse;">
                    <thead>
                        <tr style="background:#212529;color:white;">
                            <th style="padding:10px;text-align:left;">Rank</th>
                            <th style="padding:10px;text-align:left;">Trek Name</th>
                            <th style="padding:10px;text-align:center;">Bookings</th>
                        </tr>
                    </thead>
                    <tbody>{popular_rows}</tbody>
                </table>
            </div>
            <div style="background:#212529;padding:12px 20px;border-radius:0 0 8px 8px;text-align:center;">
                <p style="color:#adb5bd;font-size:12px;margin:0;">
                    Auto-generated by Trekking Management Application
                </p>
            </div>
        </body></html>
        """

        admin = User.query.filter_by(role='admin').first()
        admin_email = current_app.config.get('ADMIN_EMAIL', admin.email)

        msg = Message(
            subject=f'📊 Monthly Trekking Report — {month_label}',
            recipients=[admin_email],
            html=html_body
        )
        mail.send(msg)

        return jsonify({
            'message': f'Monthly report for {month_label} sent to {admin_email} successfully.'
        }), 200

    except Exception as e:
        print(f'Report error: {str(e)}')
        return jsonify({
            'error': f'Failed to send report: {str(e)}'
        }), 500