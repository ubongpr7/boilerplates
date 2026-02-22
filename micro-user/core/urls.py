from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from schema_graph.views import Schema

schema_view = get_schema_view(
   openapi.Info(
      title="user service API Docs",
      default_version='v1',
      description="Core User Management endpoints",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email=f"contact@{(settings.PLATFORM_NAME or 'platform').lower()}.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    #  api endpoints docs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("schema/", Schema.as_view()),

    # djoser urls
    path('', include('djoser.urls'),name='djoser_users'),
    path('auth/', include("mainapps.accounts.jwt_urls")),
    path('accounts/', include("mainapps.accounts.urls")),
    # feature apps
    # path('profiles/', include("mainapps.profiles.urls")),

    # Integrations
]+static(
    settings.MEDIA_URL,document_root=settings.MEDIA_ROOT
)

