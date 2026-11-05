from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView ,TokenRefreshView

from .views import  EditView

urlpatterns = [
    path('login/' ,TokenObtainPairView.as_view(), name = 'token_abtain_pair' ),
    path('token/refresh/' ,TokenRefreshView.as_view(), name = 'token_refresh' ),
    path('edit/' ,EditView.as_view(), name = 'edit' ),
]
