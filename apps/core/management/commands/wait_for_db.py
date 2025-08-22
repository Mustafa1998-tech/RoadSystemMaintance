import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        max_retries = 30
        retry_count = 0

        while not db_conn and retry_count < max_retries:
            try:
                # Try to connect to the database
                db_conn = connections['default']
                # Try to execute a simple query
                with db_conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('Database is available!'))
                return
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
                retry_count += 1

        # If we get here, we couldn't connect to the database
        self.stdout.write(
            self.style.ERROR('Could not connect to the database after multiple attempts.')
        )
        raise Exception('Database connection failed')
