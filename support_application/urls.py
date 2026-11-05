from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("chat/", include("chat.urls")),
    path("tickets/", include("tickets.urls")),
    path("statistics/", include("Statistics.urls")),
    path("silk/", include("silk.urls", namespace="silk")),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    path(
        'swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger',
    ),

    path(
        'redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),

]