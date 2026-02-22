from rest_framework import serializers
from .models import UserProfile, ProfessionalAffiliation, EducationHistory, DeviceSync


class ProfessionalAffiliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalAffiliation
        fields = [
            'id', 'institution_name', 'affiliation_type', 'department',
            'position', 'start_date', 'end_date', 'is_current',
            'verification_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EducationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationHistory
        fields = [
            'id', 'degree', 'institution', 'field_of_study',
            'graduation_date', 'gpa', 'honors', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DeviceSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceSync
        fields = [
            'id', 'device_id', 'device_type', 'device_name',
            'os_version', 'app_version', 'last_sync', 'is_active', 'created_at'
        ]
        read_only_fields = ['last_sync', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    affiliations = ProfessionalAffiliationSerializer(many=True, read_only=True)
    education_history = EducationHistorySerializer(many=True, read_only=True)
    devices = DeviceSyncSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'bio', 'profile_picture', 'gender', 'date_of_birth',
            'phone_number','language_preference', 'affiliations',
            'education_history', 'devices', 'created_at', 'updated_at',
             'role',
        ]
        read_only_fields = ['id','created_at', 'updated_at', ]
