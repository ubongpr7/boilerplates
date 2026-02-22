import base64
from io import BytesIO

import pyotp
import qrcode
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import login, logout
from django.db.models import Q
from django.utils import timezone
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from subapps.email_system.emails import send_html_email
from .models import User, VerificationCode
from djoser.social.views import ProviderAuthView
from django.contrib.auth import get_user_model

from .serializers import SocialJWTSerializer
from django.conf import settings
from .serializers import (
    MyUserSerializer as UserSerializer,
     UserUpdateSerializer, 
     TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework_simplejwt.tokens import RefreshToken




class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """User management ViewSet"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', ]:
            return UserUpdateSerializer
        # if self.action == 'quota_meta_data':
        #     return UserQuotaMetadataSerializer
        # return super().get_serializer_class()    
    
    @action(detail=False, methods=['get'], url_path='quota-meta-data')
    def quota_meta_data(self, request):
        meta_data = request.user.meta_data or {}
        serializer = self.get_serializer(instance=meta_data)
        return Response(serializer.data)
    
    def get_queryset(self):
        if  not self.request.user.is_authenticated:
            return User.objects.none()
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'detail': 'Only staff can delete users.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get', ])
    def me(self, request):
        """Get or update user profile"""
        return Response(UserSerializer(request.user).data)
    
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users"""
        query = request.query_params.get('q', '')
        if query:
            queryset = User.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            ).filter(is_active=True)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response([])



class VerificationAPI(APIView):
    throttle_classes = [AnonRateThrottle]
    def post(self, request):
        """Handle both sending verification code and verifying code submission (POST)"""
        action = request.data.get('action')

        if action == 'send_code':
            return self.send_verification_code(request)
        elif action == 'verify_code':
            return self.verify_code(request)
        else:
            return Response(
                {"error": "Invalid action. Use 'send_code' or 'verify_code'."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def send_verification_code(self, request):
        """Send verification code via email"""
        email = request.data.get('email')

        if not email:
            return Response(
                {"error": "Email parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            code, created = VerificationCode.objects.get_or_create(
                user=user,
                verification_type='email'
            )
            code.save()  # Ensure the code is saved or updated
            
            send_html_email(
                subject=f'Your Verification Code: {code.code}',
                message=f'Use this code to verify your login: {code.code}',
                to_email=[user.email],
                html_file='accounts/verify.html'
            )
            
            return Response(
                {"message": "Verification code sent successfully"},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {"error": "User  not found with this email"},
                status=status.HTTP_404_NOT_FOUND
            )

    def verify_code(self, request):
        """Verify code submission"""
        email = request.data.get('email')
        code_input = request.data.get('code')
        
        if not email or not code_input:
            return Response(
                {"error": "Both email and code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)

            verification_code = VerificationCode.objects.get(user=user, verification_type='email')
            if not verification_code.is_valid():
                return Response(
                    {"error": "Verification code has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if str(verification_code.code) != code_input.strip():
                return Response(
                    {"error": "Invalid verification code"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            verification_code.delete()
            return Response(
                {
                    "message": "Verification successful",
                    "user_id": user.id,
                    "email": user.email
                },
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {"error": "User  not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except VerificationCode.DoesNotExist:
            return Response(
                {"error": "No active verification code for this user"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomProviderAuthView(ProviderAuthView):
    serializer_class = SocialJWTSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            role = (request.query_params.get('role') or '').strip().lower()

            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            
            if role and refresh_token and role !='candidate':
                try:
                    refresh = RefreshToken(refresh_token)
                    user_id = refresh.get('user_id')
                except Exception:
                    user_id = None

                if user_id :
                    user = User.objects.filter(id=user_id).first()
                    valid_roles = {choice[0] for choice in User._meta.get_field('role').choices}
                    if user and role in valid_roles and user.role in ['', None, user._meta.get_field('role').default]:
                        user.role = role
                        user.save(update_fields=['role'])

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response

class MfaSetupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.user.id)
        force = str(request.data.get('force', '')).strip().lower() in {'1', 'true', 'yes'}

        if user.mfa_enabled and not force and user.has_setup_mfa:
            return Response(
                {"detail": "MFA is already enabled for this account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if force or not user.mfa_secret:
            user.mfa_secret = pyotp.random_base32()
            user.mfa_enabled = False
            user.save(update_fields=['mfa_secret', 'mfa_enabled'])

        issuer = getattr(
            settings,
            "MFA_ISSUER",
            getattr(settings, "PLATFORM_NAME", None) or getattr(settings, "SITE_NAME", None) or "Platform",
        )
        totp = pyotp.TOTP(user.mfa_secret)
        otpauth_url = totp.provisioning_uri(name=user.email, issuer_name=issuer)

        qr_image = qrcode.make(otpauth_url)
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_data = base64.b64encode(buffer.getvalue()).decode("ascii")

        return Response(
            {
                "mfa_secret": user.mfa_secret,
                "otpauth_url": otpauth_url,
                "qr_code": f"data:image/png;base64,{qr_data}",
                "mfa_enabled": user.mfa_enabled,
                "has_setup_mfa": user.has_setup_mfa,
            },
            status=status.HTTP_200_OK
        )


class MfaVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.user.id)
        code = (request.data.get('code') or '').strip()

        if not code:
            return Response(
                {"detail": "Verification code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.mfa_secret:
            return Response(
                {"detail": "MFA has not been set up for this account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(code, valid_window=1):
            return Response(
                {"detail": "Invalid verification code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.mfa_enabled or not user.has_setup_mfa:
            user.mfa_enabled = True
            user.has_setup_mfa = True
            user.save(update_fields=['mfa_enabled', 'has_setup_mfa'])

        return Response(
            {"detail": "MFA verified successfully.", "mfa_enabled": True},
            status=status.HTTP_200_OK
        )


class MfaToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.user.id)
        desired = request.data.get('enabled', None)

        if desired is None:
            desired = not user.mfa_enabled
        else:
            desired = str(desired).strip().lower() in {'1', 'true', 'yes'}

        if desired and user.mfa_enabled:
            return Response(
                {"detail": "MFA is already enabled for this account.", "mfa_enabled": True},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not desired and not user.mfa_enabled:
            return Response(
                {"detail": "MFA is already disabled for this account.", "mfa_enabled": False},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.mfa_secret:
            return Response(
                {"detail": "MFA has not been set up for this account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        code = (request.data.get('code') or '').strip()
        if not code:
            return Response(
                {"detail": "Verification code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(code, valid_window=1):
            return Response(
                {"detail": "Invalid verification code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.mfa_enabled = desired
        if desired:
            user.has_setup_mfa = True
        user.save(update_fields=['mfa_enabled', 'has_setup_mfa'])

        state = "enabled" if desired else "disabled"
        return Response(
            {"detail": f"MFA {state} successfully.", "mfa_enabled": user.mfa_enabled},
            status=status.HTTP_200_OK
        )
