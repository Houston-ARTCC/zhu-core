from django.urls import path

from . import views

urlpatterns = [
    path('', views.VisitingListView.as_view()),
    path('<int:application_id>/', views.VisitingInstanceView.as_view()),
]
