from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quickreplies.views import QuickReplyViewSet

router = DefaultRouter()
router.register("", QuickReplyViewSet, basename="quickreply")

urlpatterns = [path("", include(router.urls))]
