from django.urls import path

from . import views

urlpatterns = [
    path('', views.FeedbackListView.as_view()),
    path('<int:feedback_id>/', views.FeedbackInstanceView.as_view()),
]
