from django.urls import path

from . import views

urlpatterns = [
    path('', views.BookingListView.as_view()),
    path('<int:booking_id>/', views.BookingInstanceView.as_view()),
]
