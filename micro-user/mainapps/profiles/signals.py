from django.db.models.signals import post_save
from django.dispatch import receiver

from mainapps.profiles.models import UserProfile
from subapps.kafka.producers.accounts import examiner_profile_updated_producer, candidate_profile_updated_producer


@receiver(post_save, sender=UserProfile)
def publish_examiner_profile_update(sender, instance, **kwargs):
    examiner_profile_updated_producer(instance.user, instance)
    candidate_profile_updated_producer(instance.user, instance)
