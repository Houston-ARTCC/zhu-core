from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from zhu_core.scheduler import start_scheduler

urlpatterns = [
    path('api/administration/', include('apps.administration.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
    path('api/booking/', include('apps.booking.urls')),
    path('api/calendar/', include('apps.calendar.urls')),
    path('api/connections/', include('apps.connections.urls')),
    path('auth/', include('apps.vatsim.urls')),
    path('api/events/', include('apps.events.urls')),
    path('api/feedback/', include('apps.feedback.urls')),
    path('api/loa/', include('apps.loa.urls')),
    path('api/resources/', include('apps.resources.urls')),
    path('api/tmu/', include('apps.tmu.urls')),
    path('api/training/', include('apps.training.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/visit/', include('apps.visit.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


start_scheduler()
