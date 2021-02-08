from django.conf.urls import url
from .views import ReminderCreate, GetMsisdnTimezoneTurn

urlpatterns = [
    url(
        r"^reminders",
        ReminderCreate.as_view(),
        name="reminder-create",
    ),
    url(
        r"^timezone/turn",
        GetMsisdnTimezoneTurn.as_view(),
        name="timezone-check-turn",
    ),
]
