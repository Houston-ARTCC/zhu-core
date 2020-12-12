from django.urls import path

from . import views

urlpatterns = [
    path('', views.FeedbackListView.as_view()),
]
