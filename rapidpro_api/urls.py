from django.urls import include, path
from rest_framework.routers import DefaultRouter

from rapidpro_api.views import ProfileSyncViewSet

router = DefaultRouter()
router.register("", ProfileSyncViewSet, basename="profileSync")

urlpatterns = [path("", include(router.urls))]
