from django.urls import path

from . import views

urlpatterns = [
    path("notifications/", views.NotificationView.as_view()),
    path("audit/", views.AuditLogView.as_view()),
]
