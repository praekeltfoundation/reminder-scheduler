from django.urls import path
from django.conf.urls import url
from .views import ReminderCreate

urlpatterns = [
    url(
        r"^reminders",
        ReminderCreate.as_view(),
        name="reminder-create",
    ),
]
