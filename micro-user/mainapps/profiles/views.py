from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile, ProfessionalAffiliation, EducationHistory, DeviceSync
from .serializers import (
    UserProfileSerializer, ProfessionalAffiliationSerializer,
    EducationHistorySerializer, DeviceSyncSerializer
)


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return UserProfile.objects.none()
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return self.request.user.profile
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def register_device(self, request):
        profile = self.get_object()
        serializer = DeviceSyncSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfessionalAffiliationViewSet(viewsets.ModelViewSet):
    serializer_class = ProfessionalAffiliationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ProfessionalAffiliation.objects.none()
        return ProfessionalAffiliation.objects.filter(user_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user_profile=self.request.user.profile)


class EducationHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = EducationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return EducationHistory.objects.none()
        return EducationHistory.objects.filter(user_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user_profile=self.request.user.profile)


class DeviceSyncViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSyncSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return DeviceSync.objects.none()
        return DeviceSync.objects.filter(user_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user_profile=self.request.user.profile)
