from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from . import views

urlpatterns = [
    path('token/', views.process_oauth),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view()),
]
