from django.core.management.base import BaseCommand

from subapps.kafka.consumers.consumer import consume_events


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        consume_events()
