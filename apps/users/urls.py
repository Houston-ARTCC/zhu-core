from django.urls import path

from . import views

urlpatterns = [
    path("", views.ActiveUserListView.as_view()),
    path("<int:cid>/", views.UserInstanceView.as_view()),
    path("<int:cid>/feedback/", views.UserFeedbackView.as_view()),
    path("simplified/", views.SimplifiedActiveUserListView.as_view()),
    path("all/", views.AllUserListView.as_view()),
    path("newest/", views.NewestUserListView.as_view()),
    path("staff/", views.StaffListView.as_view()),
]
