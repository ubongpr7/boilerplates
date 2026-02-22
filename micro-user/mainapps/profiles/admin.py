from django.contrib import admin
from .models import UserProfile, ProfessionalAffiliation, EducationHistory, DeviceSync

class ProfessionalAffiliationInline(admin.TabularInline):
    model = ProfessionalAffiliation
    extra = 1
    readonly_fields = ('created_at', 'updated_at')

class EducationHistoryInline(admin.TabularInline):
    model = EducationHistory
    extra = 1
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender', 'date_of_birth', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProfessionalAffiliationInline, EducationHistoryInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'profile_picture', 'bio')
        }),
        ('Personal Information', {
            'fields': ('gender', 'date_of_birth')
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Preferences', {
            'fields': ('language_preference',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(ProfessionalAffiliation)
class ProfessionalAffiliationAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'institution_name', 'position', 'verification_status', 'start_date', 'end_date', 'is_current')
    list_filter = ('verification_status', 'affiliation_type', 'is_current')
    search_fields = ('institution_name', 'user_profile__user__email', 'position')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user_profile', 'institution_name', 'position')
        }),
        ('Affiliation Details', {
            'fields': ('affiliation_type', 'department', 'start_date', 'end_date', 'is_current')
        }),
        ('Verification', {
            'fields': ('verification_status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(EducationHistory)
class EducationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'degree', 'institution', 'graduation_date', 'field_of_study')
    list_filter = ('degree', 'graduation_date')
    search_fields = ('institution', 'user_profile__user__email', 'field_of_study')
    date_hierarchy = 'graduation_date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user_profile', 'degree', 'institution')
        }),
        ('Education Details', {
            'fields': ('field_of_study', 'graduation_date', 'gpa', 'honors')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(DeviceSync)
class DeviceSyncAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'device_name', 'device_type', 'is_active', 'last_sync', 'os_version', 'app_version')
    list_filter = ('device_type', 'is_active')
    search_fields = ('device_id', 'device_name', 'user_profile__user__email')
    date_hierarchy = 'last_sync'
    readonly_fields = ('created_at', 'last_sync')

    fieldsets = (
        (None, {
            'fields': ('user_profile', 'device_name', 'device_id')
        }),
        ('Device Information', {
            'fields': ('device_type', 'os_version', 'app_version')
        }),
        ('Sync Status', {
            'fields': ('is_active', 'last_sync')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
