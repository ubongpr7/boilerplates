import json
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from .models import User, VerificationCode, Address

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined','role','has_onboarded','mfa_enabled', 'has_setup_mfa')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    date_hierarchy = 'date_joined'
    readonly_fields = ('date_joined', 'last_login', 'meta_data_pretty')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'sex', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions','role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Contact Information', {'fields': ('phone_number',)}),
        ('Subscription metadata', {'fields': ('meta_data_pretty',)}),
        ('Security', {'fields': ('mfa_enabled', 'has_setup_mfa')}),
    )


    def meta_data_pretty(self, obj):
        """Render JSON metadata in a readable block."""
        if not obj.meta_data:
            return "-"
        formatted = json.dumps(obj.meta_data, indent=2, sort_keys=True)
        return mark_safe(f"<pre>{formatted}</pre>")

    meta_data_pretty.short_description = "Meta Data"

@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'verification_type', 'expires_at', 'is_valid')
    list_filter = ('verification_type',)
    search_fields = ('user__email',)
    readonly_fields = ('user', 'code', 'verification_type', 'expires_at', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'region', 'country', 'postal_code')
    list_filter = ('country', 'region')
    search_fields = ('street', 'city', 'postal_code')
