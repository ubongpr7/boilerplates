from decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import ValidationError
from .models import User, VerificationCode
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as BaseTokenRefreshSerializer


from djoser.social.serializers import ProviderAuthSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):


    @classmethod
    def get_all_permissions(cls, user):
        user_perms = set()
        
        # Add user permissions
        user_perms.update(user.user_permissions.all().values_list('codename', flat=True))
        
        # Add group permissions
        for group in user.groups.all():
            user_perms.update(group.permissions.all().values_list('codename', flat=True))
        
        
        
        return user_perms
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Get user permissions
        perms = cls.get_all_permissions(user)
        token['permissions'] = list(perms)
        token['email'] = user.email
        token['user_id'] = user.id
        meta = user.meta_data or {}
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['is_active'] = user.is_active
        token['mfa_enabled'] = user.mfa_enabled
        token['has_setup_mfa'] = user.has_setup_mfa
        
        return token

    def validate(self, attrs):
        """Validate and return enhanced user data"""
        email = attrs.get(self.username_field) or attrs.get("email")
        password = attrs.get("password")

        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()

        if not user:
            raise AuthenticationFailed("No account found with this email.", code="email_not_found")
        if not user.is_active:
            raise AuthenticationFailed("Your email is yet to be verified. Check your inbox for a verification link.", code="account_disabled")
        
        if password and not user.check_password(password):
            raise AuthenticationFailed("Incorrect password.", code="password_mismatch")

        data = super().validate(attrs)
        user = self.user
        data.update({
            'user': user.get_full_name,
            "permissions": self.get_all_permissions(user),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            'mfa_enabled': user.mfa_enabled,
            'has_setup_mfa': user.has_setup_mfa,
            'profile_picture': user.profile.profile_picture.url if user.profile and user.profile.profile_picture    else None


        })
        
        return data


class SocialJWTSerializer(ProviderAuthSerializer):
    """
    Override Djoser social provider serializer to mint our JWTs (with custom claims).
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        user = data.get("user") or getattr(self, "user", None) or self.context.get("request").user
        if not user or not user.is_authenticated:
            raise ValidationError("Unable to resolve authenticated user for social login.")
        # keep only the user; create() will build tokens
        return {"user": user}

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = MyTokenObtainPairSerializer.get_token(user)
        return {
            "user": user,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class TokenRefreshSerializer(BaseTokenRefreshSerializer):
    """Attach custom claims to refreshed access tokens."""

    @classmethod
    def get_all_permissions(cls, user):
        user_perms = set()
        
        # Add user permissions
        user_perms.update(user.user_permissions.all().values_list('codename', flat=True))
        
        # Add group permissions
        for group in user.groups.all():
            user_perms.update(group.permissions.all().values_list('codename', flat=True))
        
        
    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get("request")
        user_id = request.user.id if request else None

        user = getattr(request, "user", None) if request else None

        raw_refresh = data.get("refresh") or attrs.get("refresh")

        if (not user or not user.is_authenticated) and raw_refresh:
            try:
                refresh_token = RefreshToken(raw_refresh)
                user_id = refresh_token.get("user_id")
                if user_id:
                    user = User.objects.filter(id=user_id).first()
            except Exception:
                user = None

        if user and user.is_authenticated:
            custom_refresh = MyTokenObtainPairSerializer.get_token(user)
            data["access"] = str(custom_refresh.access_token)
            if "refresh" in data:
                data["refresh"] = str(custom_refresh)

            meta = user.meta_data or {}
            plan_name = (meta.get("plan") or {}).get("slug")
            exam_meta = (meta.get("plan_features") or {}).get("exam_attempts") or {}
            simulations_left = exam_meta.get("limit_value")

            data.update({
                'user': user.get_full_name,
                'has_onboarded': user.has_onboarded,
                'permissions': self.get_all_permissions(user),
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'mfa_enabled': user.mfa_enabled,
                'has_setup_mfa': user.has_setup_mfa,
                'profile_picture': user.profile.profile_picture.url if user.profile and user.profile.profile_picture    else None

            })
        return data



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name','role']
        ref_name = "AccountsUser"

class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = ['id', 'user', 'code', 'verification_type', 'expires_at', 'created_at']
        read_only_fields = ['code', 'expires_at', 'created_at']



class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password',)
        
    def create(self, validated_data):
        
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        
        # Create the user with explicit parameters
        user = User.objects.create_user(
            email=validated_data['email'].lower(),
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
        )
        return user






class MyUserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'get_full_name','role'
        )
        read_only_fields = (
            'id', 'get_full_name',
        )

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 
        )

    

