# alx_travel_app

A Django REST Framework (DRF) project for managing travel listings, bookings, reviews, **and payments via Chapa API**, now extended with **Celery and RabbitMQ** to handle background email notifications asynchronously.

---

## Features

- **Listings**: Create, view, update, and delete travel listings.  
- **Bookings**: Book listings and trigger background confirmation emails.  
- **Payments (New)**: Integrated **Chapa API** for secure payment processing.  
- **Email Notifications (New)**: Booking confirmation emails sent asynchronously via **Celery with RabbitMQ**.  
- **API Documentation**: Built-in Swagger and ReDoc endpoints.  

---

## Celery & RabbitMQ Integration

### 1️⃣ Install Dependencies

```bash
pip install celery==5.3.6 django-celery-results
sudo apt install rabbitmq-server  # For Linux
```

---

### 2️⃣ Configuration

**In `alx_travel_app/settings.py`:**

```python
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest:guest@localhost//')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='rpc://')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

---

### 3️⃣ Celery Setup

**File: `alx_travel_app/celery.py`**

```python
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')

app = Celery('alx_travel_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

**File: `alx_travel_app/__init__.py`**

```python
from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

__all__ = ('celery_app',)
```

---

### 4️⃣ Task Definition

**File: `listings/tasks.py`**

```python
from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime

@shared_task
def send_booking_confirmation_email(user_email, listing_title, check_in, check_out):
    subject = "Booking Confirmation"
    message = (
        f"Your booking for '{listing_title}' has been confirmed!\n\n"
        f"Check-in Date: {check_in}\n"
        f"Check-out Date: {check_out}\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "Thank you for booking with us!"
    )
    from_email = "no-reply@alxtravel.com"
    send_mail(subject, message, from_email, [user_email])
    return f"Confirmation email sent to {user_email}"
```

---

### 5️⃣ Trigger Task in Views

In **`listings/views.py`**, after booking creation:

```python
from .tasks import send_booking_confirmation_email

send_booking_confirmation_email.delay(
    request.user.email,
    booking.listing.title,
    booking.check_in,
    booking.check_out
)
```

---

### 6️⃣ Run Services

Start the services in three separate terminals:

```bash
sudo service rabbitmq-server start
celery -A alx_travel_app worker --loglevel=info
python manage.py runserver
```

---

## Email Configuration

For local testing:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

For production (Gmail SMTP):

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

---

## Testing the Flow

1. Create a booking via `/api/bookings/`  
2. Watch Celery terminal — it should log email task success  
3. Check email (or console output for local backend)  

---

## API Documentation

- Swagger UI → `http://127.0.0.1:8000/swagger/`  
- ReDoc → `http://127.0.0.1:8000/redoc/`

---

## Tech Stack

- **Python 3.x**, **Django 5.x**  
- **Django REST Framework**, **Celery**, **RabbitMQ**  
- **drf-yasg** for API documentation  
- **PostgreSQL / SQLite** database  
