from django.urls import path

from . import views

urlpatterns = [
    path('', views.ScheduledSessionListView.as_view()),
    path('sessions/<int:cid>/', views.SessionListView.as_view()),
    path('sessions/<int:session_id>/', views.SessionInstanceView.as_view()),
    path('request/', views.TrainingRequestListView.as_view()),
    path('request/pending/', views.PendingTrainingRequestListView.as_view()),
    path('request/<int:request_id>/', views.TrainingRequestInstanceView.as_view()),
]
