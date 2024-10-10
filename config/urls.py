from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("scheduler.urls")),  # To be removed
    path("scheduler/", include("scheduler.urls")),  # To be removed
    path("quickreplies/", include("quickreplies.urls")),
    path("rapidpro_api/", include("rapidpro_api.urls")),
]
