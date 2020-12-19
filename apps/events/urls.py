from django.urls import path

from . import views

urlpatterns = [
    path('', views.EventListView.as_view()),
    path('<int:event_id>/', views.EventInstanceView.as_view()),
    path('position/<int:position_id>/', views.PositionInstanceView.as_view()),
    path('request/<int:position_id>/', views.RequestPositionView.as_view()),
    path('support/', views.RequestSupportView.as_view()),
    path('support/<int:request_id>/', views.SupportRequestInstanceView.as_view()),
]
