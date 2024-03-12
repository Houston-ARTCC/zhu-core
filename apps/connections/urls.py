from django.urls import path

from . import views

urlpatterns = [
    path("online/", views.OnlineControllersView.as_view()),
    path("statistics/", views.StatisticsView.as_view()),
    path("statistics/admin/", views.AdminStatisticsView.as_view()),
    path("top/controllers/", views.TopControllersView.as_view()),
    path("top/positions/", views.TopPositionsView.as_view()),
    path("sessions/<int:cid>/", views.ControllerSessionsView.as_view()),
    path("daily/<int:year>/", views.DailyStatisticsView.as_view()),
]
