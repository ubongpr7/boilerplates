from django.db import connection
from django.db.models.signals import post_save, pre_delete
from django.db.utils import OperationalError, ProgrammingError
from subapps.kafka.producers.accounts import user_created_producer, user_updated_producer, user_deleted_producer
from django.contrib.auth import get_user_model
from django.dispatch import receiver

User = get_user_model()

@receiver(pre_delete, sender=User)
def publish_user_deleted_event(sender, instance, **kwargs):
    """
    Publish user deleted event to Kafka.
    """
    user_deleted_producer(instance)


@receiver(pre_delete, sender=User)
def cleanup_notification_preferences(sender, instance, **kwargs):
    """
    Remove legacy communication preferences so the FK constraint does not block user deletion.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM communication_notificationpreference WHERE user_id = %s",
                [instance.pk],
            )
    except (ProgrammingError, OperationalError):
        # Table does not exist (communication service removed); nothing to clean up.
        pass

from mainapps.profiles.models import UserProfile
from .models import VerificationCode

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)



@receiver(post_save,sender=User)
def post_save_create_user_code(sender, instance, created,**kwargs):
    if created:
        VerificationCode.objects.create(user=instance)

@receiver(post_save, sender=User)
def publish_user_events(sender, instance, created, **kwargs):
    """
    Publish user created/updated events to Kafka.
    """
    if created:
        user_created_producer(instance)
    else:
        # This is a simplified version. In a real application, you would
        # want to check which fields have been updated to decide if an
        # event needs to be published.
        updated_fields = ['email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active'] # Example fields
        user_updated_producer(instance, updated_fields)
