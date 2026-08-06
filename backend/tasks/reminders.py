from celery_app import celery
from models.booking import Booking
from models.trek import Trek
from datetime import date, timedelta
from flask_mail import Message
from extensions import mail


def send_reminder_email(user, trek):
    """
    Sends an HTML email reminder to a user about their upcoming trek.
    """
    subject = f"🏔️ Reminder: Your trek '{trek.trek_name}' starts soon!"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">

        <div style="background-color: #212529; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0;">🏔️ Trekking Management</h1>
        </div>

        <div style="padding: 30px; background-color: #f8f9fa; border: 1px solid #dee2e6;">
            <h2>Hello {user.full_name}!</h2>
            <p>This is a reminder that your upcoming trek is approaching.</p>

            <table style="width:100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background-color: #e9ecef;">
                    <td style="padding: 10px; font-weight: bold;">Trek Name</td>
                    <td style="padding: 10px;">{trek.trek_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-weight: bold;">Location</td>
                    <td style="padding: 10px;">📍 {trek.location}</td>
                </tr>
                <tr style="background-color: #e9ecef;">
                    <td style="padding: 10px; font-weight: bold;">Start Date</td>
                    <td style="padding: 10px;">🗓️ {trek.start_date}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-weight: bold;">End Date</td>
                    <td style="padding: 10px;">🗓️ {trek.end_date}</td>
                </tr>
                <tr style="background-color: #e9ecef;">
                    <td style="padding: 10px; font-weight: bold;">Difficulty</td>
                    <td style="padding: 10px;">{trek.difficulty}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-weight: bold;">Duration</td>
                    <td style="padding: 10px;">⏱️ {trek.duration_days} days</td>
                </tr>
            </table>

            <div style="background-color: #fff3cd; border: 1px solid #ffc107;
                        padding: 15px; border-radius: 6px; margin: 20px 0;">
                <strong>📋 Important Instructions:</strong><br>
                {trek.instructions or 'Please be well prepared. Carry essentials including water, first aid, and appropriate clothing.'}
            </div>

            <p style="color: #6c757d; font-size: 14px;">
                Safe trekking! Please reach the assembly point on time.<br>
                — Trekking Management Team
            </p>
        </div>

        <div style="background-color: #212529; padding: 10px 20px;
                    border-radius: 0 0 8px 8px; text-align: center;">
            <p style="color: #adb5bd; font-size: 12px; margin: 0;">
                This is an automated reminder from the Trekking Management Application.
            </p>
        </div>

    </body>
    </html>
    """

    try:
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body
        )
        mail.send(msg)
        print(f"✅ Reminder sent to {user.email} for trek: {trek.trek_name}")
    except Exception as e:
        print(f"❌ Failed to send reminder to {user.email}: {e}")


@celery.task
def send_daily_reminders():
    """
    Scheduled daily at 8 AM.
    Finds all treks starting within the next 3 days
    and sends email reminders to all booked users.
    """
    print("🔔 Running daily reminder job...")

    upcoming_date = date.today() + timedelta(days=3)

    upcoming_treks = Trek.query.filter(
        Trek.status == 'Open',
        Trek.start_date <= upcoming_date,
        Trek.start_date >= date.today()
    ).all()

    if not upcoming_treks:
        print("ℹ️  No upcoming treks in the next 3 days.")
        return

    reminder_count = 0
    for trek in upcoming_treks:
        bookings = Booking.query.filter_by(
            trek_id=trek.id,
            status='Booked'
        ).all()

        for booking in bookings:
            user = booking.user
            send_reminder_email(user, trek)
            reminder_count += 1

    print(f"✅ Daily reminders done. {reminder_count} email(s) sent.")