from django.urls import path

from . import views

urlpatterns = [
    path("", views.EventsListView.as_view()),
    path("archived/", views.ArchivedEventsListView.as_view()),
    path("<int:event_id>/", views.EventInstanceView.as_view()),
    path("position/<int:position_id>/", views.PositionInstanceView.as_view()),
    path("request/<int:shift_id>/", views.ShiftRequestView.as_view()),
    path("shift/<int:shift_id>/", views.ShiftInstanceView.as_view()),
    path("support/", views.SupportRequestListView.as_view()),
    path("support/<int:request_id>/", views.SupportRequestInstanceView.as_view()),
    path("presets/", views.PositionPresetListView.as_view()),
    path("presets/<int:preset_id>/", views.PositionPresetInstanceView.as_view()),
    path("scores/", views.EventScoreListView().as_view()),
    path("scores/<int:cid>/", views.EventScoreListView().as_view()),
]
