from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, ProfessionalAffiliationViewSet,
    EducationHistoryViewSet, DeviceSyncViewSet
)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')
# router.register(r'affiliations', ProfessionalAffiliationViewSet, basename='affiliation')
# router.register(r'education', EducationHistoryViewSet, basename='education')
# router.register(r'devices', DeviceSyncViewSet, basename='device')

urlpatterns = [
    path('', include(router.urls)),
]
