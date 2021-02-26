from django.urls import path

from . import views

urlpatterns = [
    path('', views.SessionListView.as_view()),
]
