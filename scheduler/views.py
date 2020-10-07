from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from .models import ReminderSchedule, ReminderContent

class ReminderCreate(APIView):
    queryset = ReminderSchedule.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            recipient_id = request.data['contacts'][0]['wa_id']
        except KeyError:
            status = 400
            message = {"contacts.0.wa_id": ["This field is required."]}
            return Response(message, status=status)

        content = ReminderContent.objects.last()

        # Default to 23 hours but allow us to overwrite it
        delay = int(request.GET.get('hour_delay', 23))
        scheduled_for = timezone.now() + timedelta(hours=delay)
        new_reminder = ReminderSchedule.objects.create(
            schedule_time=scheduled_for,
            recipient_id=recipient_id,
            content=content
        )

        existing_reminders = ReminderSchedule.objects.filter(
            recipient_id=recipient_id,
            sent_time__isnull=True,
            cancelled=False).exclude(pk=new_reminder.pk).update(
                cancelled=True
            )

        return Response({"accepted": True}, status=201)
