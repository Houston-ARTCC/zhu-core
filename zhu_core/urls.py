from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.vatsim.urls')),
    path('api/events/', include('apps.events.urls')),
    path('api/feedback/', include('apps.feedback.urls')),
    path('api/resources/', include('apps.resources.urls')),
    path('api/training/', include('apps.training.urls')),
    path('api/users/', include('apps.users.urls')),
    path('admin/', admin.site.urls),
]
