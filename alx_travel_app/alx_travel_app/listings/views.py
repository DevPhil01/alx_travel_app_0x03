#!/usr/bin/env python3
"""
ViewSets for Listings, Bookings, and Payment API with Chapa integration.
"""

import os
import requests
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer

CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")
CHAPA_BASE_URL = "https://api.chapa.co/v1/transaction"


class ListingViewSet(viewsets.ModelViewSet):
    """ViewSet for Listings with full CRUD support."""
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Bookings with full CRUD support."""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


# ✅ NEW CLASS: Payment Initiation and Verification
class InitiatePaymentView(APIView):
    """Initiate payment for a booking using Chapa API."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        # Generate unique transaction reference
        tx_ref = f"CHAPA-{booking.booking_id}"

        # Check if payment already exists
        if hasattr(booking, "payment"):
            payment = booking.payment
            if payment.status == "completed":
                return Response({"message": "Payment already completed."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Create initial payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.listing.price_per_night,  # You can customize this to total nights * price_per_night
                transaction_reference=tx_ref,
                status="pending"
            )

        # Prepare Chapa payment payload
        data = {
            "amount": str(payment.amount),
            "currency": payment.currency,
            "email": booking.user.email,
            "first_name": booking.user.first_name or "Guest",
            "last_name": booking.user.last_name or "User",
            "tx_ref": tx_ref,
            "callback_url": request.build_absolute_uri(f"/api/verify-payment/{booking.booking_id}/"),
            "return_url": request.build_absolute_uri(f"/bookings/{booking.booking_id}/success/"),
            "customization": {
                "title": "Booking Payment",
                "description": f"Payment for booking {booking.booking_id}",
            },
        }

        headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}

        try:
            response = requests.post(f"{CHAPA_BASE_URL}/initialize", json=data, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                payment.chapa_tx_ref = tx_ref
                payment.save()
                return Response({
                    "checkout_url": response_data["data"]["checkout_url"],
                    "message": "Payment initialized successfully."
                })
            else:
                return Response({
                    "error": response_data.get("message", "Payment initialization failed.")
                }, status=status.HTTP_400_BAD_REQUEST)

        except requests.RequestException as e:
            return Response({"error": f"Network error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)


class VerifyPaymentView(APIView):
    """Verify payment status from Chapa API."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
        payment = getattr(booking, "payment", None)

        if not payment:
            return Response({"error": "No payment found for this booking."}, status=status.HTTP_404_NOT_FOUND)

        headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
        verify_url = f"{CHAPA_BASE_URL}/verify/{payment.transaction_reference}"

        try:
            response = requests.get(verify_url, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                chapa_status = response_data["data"]["status"]

                if chapa_status == "success":
                    payment.status = "completed"
                elif chapa_status == "failed":
                    payment.status = "failed"
                else:
                    payment.status = "pending"

                payment.save()

                return Response({
                    "booking_id": str(booking.booking_id),
                    "payment_status": payment.status,
                    "chapa_response": response_data
                })

            return Response({
                "error": response_data.get("message", "Verification failed.")
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.RequestException as e:
            return Response({"error": f"Network error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
