import json
import redis
import requests

from config.celery import app
from celery.utils.log import get_task_logger
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from urllib.parse import urljoin

from .models import ReminderSchedule


logger = get_task_logger(__name__)
r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

@app.task(ignore_result=True,)
def check_for_scheduled_reminders():
    logger.info("Checking for due reminders")

    threshold = timezone.now() + timedelta(minutes=5)
    yesterday = timezone.now() - timedelta(hours=23)
    reminders_due = ReminderSchedule.objects.filter(
        sent_time__isnull=True,
        schedule_time__lt=threshold,
        schedule_time__gt=yesterday,
        cancelled=False
    )

    for reminder in reminders_due.iterator():
        send_reminder.delay(reminder.pk)


@app.task(
    ignore_result=True,
    soft_time_limit=10,
    time_limit=15)
def send_reminder(pk):
    with r.lock("reminder_%d" % pk, timeout=10):
        # Return early if the reminder has already been sent
        try:
            reminder = ReminderSchedule.objects.get(
                pk=pk, sent_time__isnull=True, cancelled=False)
        except ReminderSchedule.DoesNotExist:
            logger.info("No unsent reminder with pk %d" % pk)
            return

        logger.info("Retrieving contact info")
        s = requests.Session()
        s.headers.update({
                "Authorization": "Bearer %s" % settings.TURN_AUTH_TOKEN,
            })
        response = s.get(urljoin(
                settings.TURN_URL, f"/v1/contacts/{reminder.recipient_id}/profile"),
            headers={"Accept": "application/vnd.v1+json",}
            )
        response.raise_for_status()

        profile = response.json()

        try:
            opted_in = profile['fields']['stress_optin'].lower()
        except (KeyError, AttributeError):
            opted_in = "no" # Assume not opted in
        try:
            day5_complete = profile['fields']['day5_complete'].lower()
        except (KeyError, AttributeError):
            day5_complete = "no" # Assume last module not complete

        if day5_complete.lower() == "next" or opted_in.lower() != "yes":
            reminder.cancelled=True
            reminder.save()
            logger.info("Cancelled reminder %d" % pk)
            return

        logger.info("Sending reminder %d" % pk)
        data = {
            "preview_url": False,
            "recipient_type": "individual",
            "to": reminder.recipient_id,
            "type": "text",
            "text": {"body": reminder.content.text}
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer %s" % settings.TURN_AUTH_TOKEN,
        }

        response = s.post(
            url=urljoin(settings.TURN_URL, "/v1/messages"),
            data=json.dumps(data),
            headers=headers,
        )
        # Expecting a 200, raise for errors.
        response.raise_for_status()

        reminder.sent_time=timezone.now()
        reminder.save()
