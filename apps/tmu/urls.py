from django.urls import path

from . import views

urlpatterns = [
    path('atis/', views.ATISListView.as_view()),
    path('tmu/', views.TMUListView.as_view()),
    path('tmu/<int:notice_id>/', views.TMUInstanceView.as_view()),
    path('metar/', views.METARListView.as_view()),
    path('metar/<str:facility>/', views.METARInstanceView.as_view()),
]
