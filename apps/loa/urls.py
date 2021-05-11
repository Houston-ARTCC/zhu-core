from django.urls import path

from . import views

urlpatterns = [
    path('', views.LOARequestListView.as_view()),
    path('<int:request_id>/', views.LOARequestInstanceView.as_view()),
]
