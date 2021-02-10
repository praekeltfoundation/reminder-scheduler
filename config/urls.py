from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("scheduler.urls")),  # To be removed
    path("scheduler/", include("scheduler.urls")),
    path("quickreplies/", include("quickreplies.urls"))
]
