from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapps.profiles'

    def ready(self):
        import mainapps.profiles.signals  # noqa: F401

    def ready(self):
        import mainapps.profiles.signals  # noqa: F401
