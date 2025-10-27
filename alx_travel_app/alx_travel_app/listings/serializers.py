#!/usr/bin/env python3
"""
Serializers for Listing and Booking models
"""

from rest_framework import serializers
from .models import Listing, Booking


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model."""

    class Meta:
        model = Listing
        fields = ["listing_id", "title", "description", "price_per_night", "location", "host", "created_at"]


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""

    class Meta:
        model = Booking
        fields = ["booking_id", "listing", "user", "check_in", "check_out", "status", "created_at"]
