import csv
import io
from models.booking import Booking


def generate_booking_csv(user_id):
    """
    Generate a CSV of all bookings for a given user.
    Returns the CSV as a string — streamed back as a file download.
    This satisfies the batch export requirement:
    the server processes all records and returns them as a file.
    """
    bookings = Booking.query.filter_by(user_id=user_id).order_by(
        Booking.booking_date.desc()
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row — matches project specification requirements
    writer.writerow([
        'User ID',
        'Trek Name',
        'Location',
        'Difficulty',
        'Start Date',
        'End Date',
        'Booking Date',
        'Booking Status'
    ])

    for b in bookings:
        writer.writerow([
            b.user_id,
            b.trek.trek_name if b.trek else 'N/A',
            b.trek.location if b.trek else 'N/A',
            b.trek.difficulty if b.trek else 'N/A',
            b.trek.start_date.isoformat() if b.trek and b.trek.start_date else 'N/A',
            b.trek.end_date.isoformat() if b.trek and b.trek.end_date else 'N/A',
            b.booking_date.strftime('%Y-%m-%d %H:%M'),
            b.status
        ])

    return output.getvalue()