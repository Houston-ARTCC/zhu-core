from django.urls import path

from . import views

urlpatterns = [
    path('events/', views.EventCalendarView.as_view()),
    path('events/<int:year>/<int:month>/', views.EventCalendarView.as_view()),
    path('training/', views.TrainingCalendarView.as_view()),
    path('training/<int:year>/<int:month>/', views.TrainingCalendarView.as_view()),
]
