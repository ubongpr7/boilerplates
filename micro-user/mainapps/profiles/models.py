from django.db import models
from django.core.validators import URLValidator
from django.utils import timezone
from django.conf import settings

class RoleChoice(models.TextChoices):
    EXAMINER = 'EXAMINER', 'Examiner'
    ADMIN = 'ADMIN', 'Admin'
    STAFF = 'STAFF', 'Staff'
    STUDENT = 'STUDENT', 'Student'


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=100, blank=True, choices=RoleChoice.choices, default=RoleChoice.STUDENT)
    language_preference = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table = 'profiles_user_profile'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name} Profile"


class ProfessionalAffiliation(models.Model):
    AFFILIATION_TYPE_CHOICES = [
        ('HOSPITAL', 'Hospital'),
        ('CLINIC', 'Clinic'),
        ('UNIVERSITY', 'University'),
        ('RESEARCH', 'Research Institute'),
        ('PRIVATE', 'Private Practice'),
        ('OTHER', 'Other'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='affiliations')
    institution_name = models.CharField(max_length=255)
    affiliation_type = models.CharField(max_length=20, choices=AFFILIATION_TYPE_CHOICES)
    department = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles_professional_affiliation'
        indexes = [
            models.Index(fields=['user_profile', 'is_current']),
            models.Index(fields=['verification_status']),
        ]
    
    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.institution_name}"


class EducationHistory(models.Model):
    DEGREE_CHOICES = [
        ('MD', 'Doctor of Medicine'),
        ('DO', 'Doctor of Osteopathic Medicine'),
        ('MBBS', 'Bachelor of Medicine, Bachelor of Surgery'),
        ('OTHER', 'Other'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='education_history')
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES)
    institution = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    graduation_date = models.DateField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    honors = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles_education_history'
        ordering = ['-graduation_date']
        indexes = [
            models.Index(fields=['user_profile']),
        ]
    
    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.degree}"


class DeviceSync(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('WEB', 'Web'),
        ('ANDROID', 'Android'),
        ('IOS', 'iOS'),
        ('TABLET', 'Tablet'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    device_name = models.CharField(max_length=255)
    os_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=50, blank=True)
    last_sync = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'profiles_device_sync'
        indexes = [
            models.Index(fields=['user_profile', 'is_active']),
            models.Index(fields=['device_id']),
        ]
    
    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.device_name}"
