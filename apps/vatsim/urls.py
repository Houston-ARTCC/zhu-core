from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from . import views

urlpatterns = [
    path("token/", views.MyTokenObtainPairView.as_view()),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view()),
    path("profile/", views.UserProfileView.as_view()),
]
