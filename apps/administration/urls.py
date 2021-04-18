from django.urls import path

from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view())
]
