from django.conf.urls import url
from .views import ReminderCreate, GetMsisdnTimezoneTurn, GetMsisdnTimezones

urlpatterns = [
    url(
        r"^reminders",
        ReminderCreate.as_view(),
        name="reminder-create",
    ),
    url(
        r"^timezone/turn",
        GetMsisdnTimezoneTurn.as_view(),
        name="get-timezone-turn",
    ),
    url(
        r"^timezones",
        GetMsisdnTimezones.as_view(),
        name="get-timezones",
    ),
]
