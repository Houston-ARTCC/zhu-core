from django.urls import path

from . import views

urlpatterns = [
    path('', views.AnnouncementListView.as_view()),
]
