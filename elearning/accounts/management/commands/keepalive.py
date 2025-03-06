import os
import time

import redis
import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Keeps the Django site and Redis instance active by periodically pinging them."

    def handle(self, *args, **options):
        # Get website URL from an environment variable; if not set, default to your deployed URL.
        website_url = os.environ.get('WEBSITE_URL', 'https://awdfinal.onrender.com/')
        # Get the Redis URL from an environment variable.
        redis_url = os.environ.get('REDIS_URL', 'redis://red-cv4erq8gph6c738vacig:6379')

        self.stdout.write(f"Pinging website: {website_url}")
        self.stdout.write(f"Pinging Redis: {redis_url}")

        while True:
            # Ping the website.
            try:
                response = requests.get(website_url, timeout=10)
                self.stdout.write(f"Website ping successful: HTTP {response.status_code}")
            except Exception as e:
                self.stdout.write(f"Website ping error: {e}")

            # Ping Redis.
            try:
                r = redis.Redis.from_url(redis_url)
                pong = r.ping()
                self.stdout.write(f"Redis ping successful: {pong}")
            except Exception as e:
                self.stdout.write(f"Redis ping error: {e}")

            # Wait for 5 minutes before pinging again.
            time.sleep(300)
