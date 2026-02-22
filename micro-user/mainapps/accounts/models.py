import os
import random
from datetime import datetime
from PIL import Image
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from cities_light.models import Country, Region, SubRegion,City
from mainapps.accounts.validators import validate_city, validate_city_belongs_to_sub_region, validate_country, validate_postal_code, validate_region, validate_region_belongs_to_country, validate_sub_region
from rest_framework import serializers

def validate_adult(value):
    """Validate user is at least 18 years old"""
    from datetime import date
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError('You must be at least 18 years old')


PREFER_NOT_TO_SAY = "not_to_mention"
SEX_CHOICES = (
    ("male", _("Male")),
    ("female", _("Female")),
    (PREFER_NOT_TO_SAY, _("Prefer not to say")),
)

from django.core.exceptions import ValidationError

def _validate_alpha_name(value):
    if not value:
        return  # allow blank values

    if not value.isalpha():
        raise ValidationError("This field should only contain letters.")




class Address(models.Model):
    
    country = models.ForeignKey(
        Country, 
        on_delete=models.CASCADE,
        verbose_name=_('Country'),
        null=True,
    )
    region = models.ForeignKey(
        Region, 
        on_delete=models.CASCADE,
        verbose_name=_('Region/State'),
        null=True,
    )
    subregion = models.ForeignKey(
        SubRegion, 
        on_delete=models.CASCADE,
        verbose_name=_('Sub region/LGA'),
        null=True,
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name=_('City/Town'),
        null=True,
     )
    apt_number = models.PositiveIntegerField(
        verbose_name=_('Apartment number'),
        null=True,
        blank=True
    )
    street_number = models.PositiveIntegerField(
        verbose_name=_('Street number'),
        null=True,
        blank=True
    )
    street = models.CharField(max_length=255,blank=False,null=True)

    postal_code = models.CharField(
        max_length=10,
        verbose_name=_('Postal code'),
        help_text=_('Postal code'),
        blank=True,
        null=True,
        validators=[validate_postal_code]
    )

    def __str__(self):
        return f'{self.street}, {self.city}, {self.region}, {self.country}'
    def clean(self):
        if self.country:
            validate_country(self.country.id)
            if self.region:
                validate_region(self.region.id)
                if self.subregion:
                    validate_sub_region(self.subregion.id)
                    if self.city:
                        validate_city(self.city.id)
                        validate_region_belongs_to_country(self.region.id, self.country.id)
                        validate_city_belongs_to_sub_region(self.city.id, self.subregion.id)


def profile_image_path(instance, filename):
    """Generate path for profile images with timestamp"""
    ext = filename.split('.')[-1]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    username = instance.user.username if hasattr(instance, 'user') and instance.user else 'unknown'
    safe_username = username.replace('@', '_').replace('.', '_')
    new_filename = f"{timestamp}_{safe_username}.{ext}"
    return os.path.join('profile_images', new_filename)



class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class RoleChoices(models.TextChoices):
    CANDIDATE = 'patient', _('Candidate')
    EXAMINER = 'doctor', _('Doctor')
    ADMIN = 'admin', _('Admin')
    INSTITUTION_ADMIN = 'institution_admin', _('Institutions Admin')

class User(AbstractUser, PermissionsMixin):
    """Custom user model for user service"""
    first_name = models.CharField(_("first name"), max_length=150, blank=True,validators=[_validate_alpha_name])
    last_name = models.CharField(_("last name "), max_length=150, blank=True,validators=[_validate_alpha_name])
    email = models.EmailField(unique=True, blank=False, null=False)
    username = models.CharField(max_length=150, unique=True, blank=True)
    
    # Personal Information
    sex = models.CharField(
        max_length=20,
        choices=SEX_CHOICES,
        default=PREFER_NOT_TO_SAY,
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(
        validators=[validate_adult],
        verbose_name='Date Of Birth',
        help_text='You must be above 18 years of age.',
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True,
        null=True
    )
    meta_data = models.JSONField(default=dict, blank=True, null=True)

    role =models.CharField(
        max_length=20, 
        blank=True, 
        choices=RoleChoices.choices, 
        default=RoleChoices.CANDIDATE
    )
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name','role']
    objects = CustomUserManager()
    has_onboarded = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)
    has_setup_mfa = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
        ]
    
    @property
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def clean(self):
        if self.username:
            self.username = self.username.lower()
        if self.email:
            self.email = self.email.lower()
        if self.first_name and not self.first_name.isalpha():
            raise ValidationError("First name should only contain letters.")
        if self.last_name and not self.last_name.isalpha():
            raise ValidationError("Last name should only contain letters.")
        if self.first_name:
            self.first_name = self.first_name.title()

        if self.last_name:
            self.last_name = self.last_name.title()

        return super().clean()
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        self.clean()
        if self.role == RoleChoices.INSTITUTION_ADMIN:
            if not self.has_onboarded:
                self.mfa_enabled = True
            self.has_onboarded = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.get_full_name


class VerificationCode(models.Model):
    """Email/SMS verification codes"""
    
    VERIFICATION_TYPES = (
        ('email', 'Email Verification'),
        ('sms', 'SMS Verification'),
        ('2fa', 'Two-Factor Authentication'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    verification_type = models.CharField(
        max_length=10,
        choices=VERIFICATION_TYPES,
        default='email'
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_verificationcode'
        indexes = [
            models.Index(fields=['user', 'verification_type',]),
        ]
    
    def save(self, *args, **kwargs):
        self.code = ''.join([str(random.randint(1, 9)) for _ in range(6)])
        self.expires_at = timezone.now() + timezone.timedelta(minutes=20)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return timezone.now() < self.expires_at
    
    def __str__(self):
        return f"{self.user.email} - {self.verification_type} - {self.code}"
