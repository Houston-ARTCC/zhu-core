from django.urls import path

from . import views

urlpatterns = [
    path('', views.ActiveUserListView.as_view()),
]
