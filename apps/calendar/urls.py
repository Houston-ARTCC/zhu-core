from django.urls import path

from . import views

urlpatterns = [
    path("", views.CalendarView.as_view()),
    path("<int:year>/<int:month>/", views.CalendarView.as_view()),
]
