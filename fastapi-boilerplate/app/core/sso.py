# app/core/sso.py
"""
SSO Configuration for Google, Microsoft, and LinkedIn using fastapi-sso
"""
import os
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from fastapi_sso.sso.linkedin import LinkedInSSO

from app.core.config import settings

# Google SSO
google_sso = None
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    google_sso = GoogleSSO(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=f"{settings.SERVER_HOST}/api/v1/auth/google/callback",
        allow_insecure_http=settings.ENVIRONMENT != "production",
    )

# Microsoft SSO
microsoft_sso = None
if settings.MICROSOFT_CLIENT_ID and settings.MICROSOFT_CLIENT_SECRET:
    microsoft_sso = MicrosoftSSO(
        client_id=settings.MICROSOFT_CLIENT_ID,
        client_secret=settings.MICROSOFT_CLIENT_SECRET,
        redirect_uri=f"{settings.SERVER_HOST}/api/v1/auth/microsoft/callback",
        allow_insecure_http=settings.ENVIRONMENT != "production",
        tenant="common",  # Use "common" for multi-tenant
    )

# LinkedIn SSO
linkedin_sso = None
if settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET:
    linkedin_sso = LinkedInSSO(
        client_id=settings.LINKEDIN_CLIENT_ID,
        client_secret=settings.LINKEDIN_CLIENT_SECRET,
        redirect_uri=f"{settings.SERVER_HOST}/api/v1/auth/linkedin/callback",
        allow_insecure_http=settings.ENVIRONMENT != "production",
    )