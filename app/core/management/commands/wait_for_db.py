import time

from django.db import connections
from django.db.utils import OperationalError
# Base command class for us to build custom management commands
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **kwargs):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                # Try to set db_conn variable to the db connection
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
