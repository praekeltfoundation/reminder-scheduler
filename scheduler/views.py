from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from .models import ReminderSchedule

class ReminderCreate(APIView):
    queryset = ReminderSchedule.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            recipient_id = request.data['contacts'][0]['wa_id']
        except KeyError:
            status = 400
            message = {"contacts.0.wa_id": ["This field is required."]}
            return Response(message, status=status)
        
        # Default to 23 hours but allow us to overwrite it
        delay = int(request.GET.get('hour_delay', 23))
        scheduled_for = timezone.now() + timedelta(hours=delay)
        ReminderSchedule.objects.create(
            schedule_time=scheduled_for,
            recipient_id=recipient_id,
            content='some reminder content'
        )

        return Response({"accepted": True}, status=201)
