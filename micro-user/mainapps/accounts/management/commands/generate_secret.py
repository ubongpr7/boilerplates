from django.core.management.base import BaseCommand
import secrets
import string


class Command(BaseCommand):
    help = "Generate a long, cryptographically secure secret key"

    def add_arguments(self, parser):
        parser.add_argument(
            "--length",
            type=int,
            default=100,
            help="Length of the secret key (default: 100)"
        )

    def handle(self, *args, **options):
        length = options["length"]

        if length < 50:
            self.stderr.write(
                self.style.ERROR("Length too short. Use at least 50 characters.")
            )
            return

        alphabet = (
            string.ascii_letters +
            string.digits +
            string.punctuation
        )

        secret_key = "".join(secrets.choice(alphabet) for _ in range(length))

        self.stdout.write(self.style.SUCCESS("Generated Secret Key:\n"))
        self.stdout.write(secret_key)
