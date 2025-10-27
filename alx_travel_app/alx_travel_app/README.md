# alx_travel_app

A Django REST Framework (DRF) project for managing travel listings, bookings, reviews, **and payments via Chapa API**.  
This project provides APIs to create, retrieve, and manage travel-related data, initiate and verify payments securely, and includes built-in API documentation.  

---

## Features

- **Listings**: Create, view, update, and delete travel listings with details such as title, description, location, price, and availability.  
- **Bookings**: Book a listing by providing user details and booking dates. View existing bookings.  
- **Reviews**: Users can leave reviews for listings, including a rating and comment.  
- **Payments (New)**: Integrated **Chapa API** to initiate and verify payments securely.  
- **Serializers**: Data representation through Django REST Framework serializers.  
- **Database Seeder**: A management command to populate the database with sample listings for testing and development.  
- **API Documentation**: Interactive Swagger UI and ReDoc interfaces for testing and exploring endpoints.  

---

## Project Structure

```
alx_travel_app/
│
├── alx_travel_app/           
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── listings/                 
│   ├── models.py             # Defines Listing, Booking, Review, and Payment models
│   ├── serializers.py        
│   ├── views.py              # ViewSets and Chapa payment integration logic
│   ├── urls.py               
│   └── management/
│       └── commands/
│           └── seed.py       
│
├── db.sqlite3
└── manage.py
```

---

## Models

### Listing
- `title` (CharField)  
- `description` (TextField)  
- `location` (CharField)  
- `price_per_night` (DecimalField)  
- `created_at` (DateTimeField)  

### Booking
- `listing` (ForeignKey → Listing)  
- `user` (ForeignKey → User)  
- `check_in` (DateField)  
- `check_out` (DateField)  
- `status` (choices: pending, confirmed, canceled)  
- `created_at` (DateTimeField)  

### Review
- `listing` (ForeignKey → Listing)  
- `user` (ForeignKey → User)  
- `rating` (IntegerField, 1–5)  
- `comment` (TextField, optional)  
- `created_at` (DateTimeField)  

### Payment (New)
- `booking` (ForeignKey → Booking)`  
- `amount` (DecimalField)`  
- `transaction_id` (CharField)`  
- `status` (choices: Pending, Completed, Failed)`  
- `reference` (CharField)`  
- `created_at` (DateTimeField)`  

---

## Chapa API Integration

### Overview
This integration allows users to securely make payments for bookings via the **Chapa Payment Gateway**.

### Environment Variables
In your `.env` file (or system environment), define:

```bash
CHAPA_PUBLIC_KEY=CHAPUBK_TEST-IU051xgahZT8VzoQoBCAAD8xWnVTNqWZ
CHAPA_SECRET_KEY=CHASECK_TEST-uAUrKkyTb8ZLOTRUaIEEiiNh0T30oQkV
CHAPA_ENCRYPTION_KEY=jOoK36AnBOjIN8zbGZfPKDOb
```

Ensure these keys are **not** committed to your GitHub repo for security.

---

### Payment Flow

1. **Initiate Payment**
   - When a user books a listing, a POST request is sent to `/api/initiate-payment/` with the booking details and amount.
   - The view contacts **Chapa’s Initiate Payment Endpoint** using your `CHAPA_SECRET_KEY`.
   - A transaction reference and payment URL are returned.
   - The Payment record is stored with status `Pending`.

2. **Verify Payment**
   - After payment completion, a GET request to `/api/verify-payment/{reference}/` checks the status from Chapa’s verification endpoint.
   - If successful, the payment status updates to `Completed`; otherwise, `Failed`.

---

### Example API Workflow

#### 1️⃣ Initiate a Payment
**POST** `/api/initiate-payment/`

**Body:**
```json
{
  "booking_id": "a2f4d980-45a2-4cc8-8df9-fcbfa1924a91",
  "amount": 2500
}
```

**Response:**
```json
{
  "payment_url": "https://checkout.chapa.co/pay/xYe82n1",
  "transaction_id": "tx-1234567890",
  "status": "Pending"
}
```

---

#### 2️⃣ Verify Payment
**GET** `/api/verify-payment/{reference}/`

**Response:**
```json
{
  "reference": "xYe82n1",
  "status": "Completed",
  "message": "Payment verified successfully"
}
```

---

### Testing with Chapa Sandbox

You can test payments in the **sandbox** mode using your test API keys (as provided above).

- Base URL: `https://api.chapa.co/v1/transaction`
- Example sandbox test card:  
  - Card: `4242 4242 4242 4242`  
  - Expiry: `12/30`  
  - CVV: `123`  

After a successful transaction, run the verification endpoint to confirm that payment records update properly in your database.

---

## Installation & Setup

Follow the same steps as before, but now add environment configuration:

```bash
pip install python-dotenv
```

Then create `.env` in your project root with your Chapa keys.

Run:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## API Endpoints

| Endpoint                        | Method | Description                                   |
|---------------------------------|--------|-----------------------------------------------|
| `/api/listings/`               | GET    | List all listings                             |
| `/api/listings/`               | POST   | Create a new listing                          |
| `/api/bookings/`               | POST   | Create a new booking                          |
| `/api/initiate-payment/`       | POST   | Initiate a new Chapa payment                  |
| `/api/verify-payment/<ref>/`   | GET    | Verify a Chapa payment status                 |

---

## API Documentation

Interactive API documentation remains available:

- **Swagger UI**: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)  
- **ReDoc**: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)  

---

## Tech Stack

- **Python 3.x**  
- **Django 5.x**  
- **Django REST Framework**  
- **drf-yasg (Swagger/ReDoc)**  
- **Chapa API (Payment Gateway)**  
- **SQLite (default, can be replaced with PostgreSQL/MySQL)**  
