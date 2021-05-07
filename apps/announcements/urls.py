from django.urls import path

from . import views

urlpatterns = [
    path('', views.AnnouncementListView.as_view()),
    path('<int:announcement_id>/', views.AnnouncementInstanceView.as_view()),
    path('recent/', views.RecentAnnouncementListView.as_view()),
]
