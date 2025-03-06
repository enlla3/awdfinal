import os
import time

import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Keeps the Django site active by periodically pinging it."

    def handle(self, *args, **options):
        # Get website URL from an environment variable; if not set, default to your deployed URL.
        website_url = os.environ.get('WEBSITE_URL', 'https://awdfinal.onrender.com/')

        self.stdout.write(f"Pinging website: {website_url}")

        while True:
            try:
                response = requests.get(website_url, timeout=10)
                self.stdout.write(f"Website ping successful: HTTP {response.status_code}")
            except Exception as e:
                self.stdout.write(f"Website ping error: {e}")
            # Wait for 5 minutes before pinging again.
            time.sleep(300)
