import json
import redis
import requests

from config.celery import app
from celery.utils.log import get_task_logger
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

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
        schedule_time__gt=yesterday
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
            reminder = ReminderSchedule.objects.get(pk=pk, sent_time__isnull=True)
        except ReminderSchedule.DoesNotExist:
            logger.info("No unsent reminder with pk %d" % pk)
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

        response = requests.post(
            url=settings.TURN_URL,
            data=json.dumps(data),
            headers=headers,
        )
        # Expecting a 200, raise for errors.
        response.raise_for_status()

        reminder.sent_time=timezone.now()
        reminder.save()
