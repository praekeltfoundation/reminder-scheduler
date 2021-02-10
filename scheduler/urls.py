from django.urls import re_path
from .views import ReminderCreate, GetMsisdnTimezoneTurn, GetMsisdnTimezones

urlpatterns = [
    re_path(
        r"^reminders",
        ReminderCreate.as_view(),
        name="reminder-create",
    ),
    re_path(
        r"^timezone/turn",
        GetMsisdnTimezoneTurn.as_view(),
        name="get-timezone-turn",
    ),
    re_path(
        r"^timezones",
        GetMsisdnTimezones.as_view(),
        name="get-timezones",
    ),
]
