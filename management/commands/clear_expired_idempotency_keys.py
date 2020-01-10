from django.core.management import BaseCommand

from ...utils import clear_expired_idempotency_keys


class Command(BaseCommand):
    help = "Delete expired Stripe idempotency keys."

    def handle(self, *args, **options):
        clear_expired_idempotency_keys()
