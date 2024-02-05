from django.urls import path

from . import views

urlpatterns = [
    path("", views.LOAListView.as_view()),
    path("<int:loa_id>/", views.LOAInstanceView.as_view()),
    path("admin/", views.LOAAdminListView.as_view()),
    path("admin/<int:loa_id>/", views.LOAAdminInstanceView.as_view()),
]
