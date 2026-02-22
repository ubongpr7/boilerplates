from django.conf import settings


def branding(request):
    platform_name = getattr(settings, "PLATFORM_NAME", None) or getattr(settings, "SITE_NAME", None) or "Platform"
    return {
        "platform_name": platform_name,
        "site_name": getattr(settings, "SITE_NAME", None) or platform_name,
    }
