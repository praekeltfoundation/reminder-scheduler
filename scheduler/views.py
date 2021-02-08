import logging
import phonenumbers
import pytz

from datetime import timedelta, datetime
from math import floor
from phonenumbers import timezone as ph_timezone

from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status

from .models import ReminderSchedule, ReminderContent

LOGGER = logging.getLogger(__name__)


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

class GetMsisdnTimezoneTurn(APIView):
    def get_400_response(self, data):
        return Response(
            data,
            status=status.HTTP_400_BAD_REQUEST,
            content_type='application/json')

    def post(self, request, *args, **kwargs):
        try:
            recipient_id = request.data['contacts'][0]['wa_id']
        except KeyError:
            return self.get_400_response({"contacts.0.wa_id": ["This field is required."]})

        try:
            msisdn = phonenumbers.parse("+{}".format(recipient_id))
        except phonenumbers.phonenumberutil.NumberParseException:
            return self.get_400_response({
                "contacts.0.wa_id": ["This value must be a phone number with a region prefix."]
            })

        if not(phonenumbers.is_possible_number(msisdn) and phonenumbers.is_valid_number(msisdn)):
            return self.get_400_response({
                "contacts.0.wa_id": ["This value must be a phone number with a region prefix."]
            })


        zones = ph_timezone.time_zones_for_number(msisdn)
        if len(zones) == 1:
            approx_tz = zones[0]
        elif len(zones) > 1:
            timezones = []
            for zone in zones:
                offset = pytz.timezone(zone).utcoffset(datetime.utcnow())
                offset_seconds = (offset.days * 86400) + offset.seconds
                timezones.append({"name": zone, "offset": offset_seconds / 3600})
            ordered_tzs = sorted(timezones, key=lambda k: k['offset'])

            approx_tz = timezones[floor(len(timezones)/2)]["name"]

            LOGGER.info("Available timezones: {}. Returned timezone: {}".format(
                timezones, approx_tz))

        return Response({"success": True, "timezone": approx_tz}, status=200)
