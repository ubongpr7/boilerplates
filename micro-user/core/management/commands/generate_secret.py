from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    help = "Generate a Django SECRET_KEY suitable for production use."

    def add_arguments(self, parser):
        parser.add_argument(
            "--env",
            action="store_true",
            help="Print as SECRET_KEY=<value> for direct .env usage.",
        )

    def handle(self, *args, **options):
        secret = get_random_secret_key()
        if options["env"]:
            self.stdout.write(f"SECRET_KEY={secret}")
            return
        self.stdout.write(secret)
