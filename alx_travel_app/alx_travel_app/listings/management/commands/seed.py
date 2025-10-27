#!/usr/bin/env python3
"""
Management command to seed database with sample listings
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing


class Command(BaseCommand):
    help = "Seed the database with sample listings data"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Ensure at least one host user exists
        host, created = User.objects.get_or_create(
            username="host_user",
            defaults={"email": "host@example.com", "password": "password123"}
        )

        sample_titles = [
            "Cozy Beach House", "Mountain Cabin", "City Apartment",
            "Luxury Villa", "Safari Tent"
        ]
        locations = ["Mombasa", "Nairobi", "Diani", "Naivasha", "Lamu"]

        for i in range(5):
            listing, created = Listing.objects.get_or_create(
                title=sample_titles[i],
                defaults={
                    "description": f"A beautiful {sample_titles[i]} in {locations[i]}",
                    "price_per_night": random.randint(50, 500),
                    "location": locations[i],
                    "host": host,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created listing: {listing.title}"))
            else:
                self.stdout.write(f"Listing already exists: {listing.title}")
