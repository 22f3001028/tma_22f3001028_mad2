from celery_app import celery
from models.trek import Trek
from models.booking import Booking
from models.user import User
from extensions import db, mail
from flask_mail import Message
from sqlalchemy import func
from datetime import datetime
from flask import current_app


@celery.task
def send_monthly_report():
    """
    Scheduled on the 1st of every month at 6 AM.
    Generates an HTML monthly activity report
    and emails it to the Admin.
    """
    print("📋 Running monthly report job...")

    now = datetime.utcnow()
    current_month = now.month
    current_year = now.year
    month_label = now.strftime('%B %Y')

    # Gather statistics
    total_treks = Trek.query.count()
    completed_treks = Trek.query.filter_by(status='Completed').count()
    open_treks = Trek.query.filter_by(status='Open').count()
    total_users = User.query.filter_by(role='user').count()

    monthly_bookings = Booking.query.filter(
        db.extract('month', Booking.booking_date) == current_month,
        db.extract('year', Booking.booking_date) == current_year
    ).count()

    monthly_participants = Booking.query.filter(
        Booking.status == 'Completed',
        db.extract('month', Booking.booking_date) == current_month,
        db.extract('year', Booking.booking_date) == current_year
    ).count()

    # Popular treks
    popular = db.session.query(
        Trek.trek_name,
        Trek.location,
        func.count(Booking.id).label('booking_count')
    ).join(Booking).group_by(Trek.id).order_by(
        func.count(Booking.id).desc()
    ).limit(5).all()

    # Build popular treks table rows
    popular_rows = ''
    for i, (name, location, count) in enumerate(popular, 1):
        medals = ['🥇', '🥈', '🥉']
        medal= medals[i - 1] if i <= 3 else str(i)
        popular_rows += f"""
        <tr style="{'background-color:#f8f9fa;' if i % 2 == 0 else ''}">
            <td style="padding:10px">{medal}</td>
            <td style="padding:10px"><strong>{name}</strong></td>
            <td style="padding:10px">{location}</td>
            <td style="padding:10px; text-align:center">
                <span style="background:#212529;color:white;
                             padding:2px 10px;border-radius:12px">
                    {count}
                </span>
            </td>
        </tr>"""

    if not popular_rows:
        popular_rows = '<tr><td colspan="4" style="padding:20px;text-align:center;color:#6c757d">No bookings recorded this month.</td></tr>'

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto;">

        <div style="background-color: #212529; padding: 24px;
                    border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0;">🏔️ Trekking Management</h1>
            <p style="color: #adb5bd; margin: 6px 0 0;">Monthly Activity Report</p>
        </div>

        <div style="padding: 30px; background-color: #ffffff;
                    border: 1px solid #dee2e6;">

            <h2 style="color: #212529;">Report for {month_label}</h2>
            <p style="color: #6c757d;">
                Generated automatically on the 1st of the month.
            </p>

            <h3 style="border-bottom: 2px solid #dee2e6; padding-bottom: 8px;">
                📊 Summary
            </h3>

            <table style="width:100%; border-collapse:collapse; margin-bottom:24px;">
                <tr style="background-color:#e9ecef;">
                    <td style="padding:12px; font-weight:bold;">Total Treks in System</td>
                    <td style="padding:12px; font-size:20px;
                               font-weight:bold;">{total_treks}</td>
                </tr>
                <tr>
                    <td style="padding:12px; font-weight:bold;">Open Treks</td>
                    <td style="padding:12px; font-size:20px;
                               color:#198754; font-weight:bold;">{open_treks}</td>
                </tr>
                <tr style="background-color:#e9ecef;">
                    <td style="padding:12px; font-weight:bold;">Completed Treks</td>
                    <td style="padding:12px; font-size:20px;
                               color:#0d6efd; font-weight:bold;">{completed_treks}</td>
                </tr>
                <tr>
                    <td style="padding:12px; font-weight:bold;">Bookings This Month</td>
                    <td style="padding:12px; font-size:20px;
                               font-weight:bold;">{monthly_bookings}</td>
                </tr>
                <tr style="background-color:#e9ecef;">
                    <td style="padding:12px; font-weight:bold;">Users Participated This Month</td>
                    <td style="padding:12px; font-size:20px;
                               font-weight:bold;">{monthly_participants}</td>
                </tr>
                <tr>
                    <td style="padding:12px; font-weight:bold;">Registered Trekkers</td>
                    <td style="padding:12px; font-size:20px;
                               font-weight:bold;">{total_users}</td>
                </tr>
            </table>

            <h3 style="border-bottom: 2px solid #dee2e6; padding-bottom: 8px;">
                🔥 Popular Treks
            </h3>

            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background-color:#212529; color:white;">
                        <th style="padding:10px; text-align:left">Rank</th>
                        <th style="padding:10px; text-align:left">Trek Name</th>
                        <th style="padding:10px; text-align:left">Location</th>
                        <th style="padding:10px; text-align:center">Bookings</th>
                    </tr>
                </thead>
                <tbody>
                    {popular_rows}
                </tbody>
            </table>

        </div>

        <div style="background-color:#212529; padding:12px 20px;
                    border-radius:0 0 8px 8px; text-align:center;">
            <p style="color:#adb5bd; font-size:12px; margin:0;">
                This report was automatically generated by the
                Trekking Management Application.
            </p>
        </div>

    </body>
    </html>
    """

    # Send to admin
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("❌ No admin found.")
        return

    admin_email = current_app.config.get('ADMIN_EMAIL', admin.email)

    try:
        msg = Message(
            subject=f"📊 Monthly Trekking Report — {month_label}",
            recipients=[admin_email],
            html=html_body
        )
        mail.send(msg)
        print(f"✅ Monthly report sent to {admin_email}")
    except Exception as e:
        print(f"❌ Failed to send report: {e}")