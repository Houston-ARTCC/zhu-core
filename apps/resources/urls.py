from django.urls import path

from . import views

urlpatterns = [
    path("", views.ResourceListView.as_view()),
    path("<int:resource_id>/", views.ResourceInstanceView.as_view()),
]
