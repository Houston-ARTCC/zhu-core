from django.urls import path

from . import views

urlpatterns = [
    path('', views.EventListView.as_view()),
    path('<int:event_id>/', views.EventInstanceView.as_view()),
    path('<int:event_id>/<int:position_id>/', views.RequestPositionView.as_view()),
]
