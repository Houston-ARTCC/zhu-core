from django.urls import path

from . import views

urlpatterns = [
    path('', views.ActiveUserListView.as_view()),
    path('<int:cid>/', views.UserInstanceView.as_view()),
]
