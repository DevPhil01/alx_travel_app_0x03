
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


@shared_task
def send_booking_confirmation_email(user_email, listing_name, booking_id):
    """
    Celery task to send a booking confirmation email asynchronously.

    Args:
        user_email (str): Email address of the booking user.
        listing_name (str): Name of the listing booked.
        booking_id (str): Unique booking ID for reference.
    """

    subject = f"Booking Confirmation - {listing_name}"
    message = (
        f"Hello,\n\n"
        f"Thank you for booking with us!\n\n"
        f"Booking ID: {booking_id}\n"
        f"Listing: {listing_name}\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Your booking has been successfully received and is being processed.\n\n"
        f"Best regards,\n"
        f"The Travel App Team"
    )

    sender = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@travelapp.com")

    try:
        send_mail(
            subject,
            message,
            sender,
            [user_email],
            fail_silently=False,
        )
        print(f"[Celery] Booking confirmation sent to {user_email}")
    except Exception as e:
        print(f"[Celery] Failed to send booking confirmation: {e}")
