import json
import logging
from datetime import datetime, timedelta
from math import floor
from urllib.parse import urljoin

import phonenumbers
import pytz
import requests
from django.conf import settings
from django.utils import timezone
from phonenumbers import timezone as ph_timezone
from rest_framework import authentication, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ReminderContent, ReminderSchedule

LOGGER = logging.getLogger(__name__)


def get_middle_tz(zones):
    timezones = []
    for zone in zones:
        offset = pytz.timezone(zone).utcoffset(datetime.utcnow())
        offset_seconds = (offset.days * 86400) + offset.seconds
        timezones.append({"name": zone, "offset": offset_seconds / 3600})
    ordered_tzs = sorted(timezones, key=lambda k: k["offset"])

    approx_tz = ordered_tzs[floor(len(ordered_tzs) / 2)]["name"]

    LOGGER.info(
        "Available timezones: {}. Returned timezone: {}".format(ordered_tzs, approx_tz)
    )
    return approx_tz


class ReminderCreate(APIView):
    queryset = ReminderSchedule.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            recipient_id = request.data["contacts"][0]["wa_id"]
        except KeyError:
            status = 400
            message = {"contacts.0.wa_id": ["This field is required."]}
            return Response(message, status=status)

        content = ReminderContent.objects.last()

        # Default to 23 hours but allow us to overwrite it
        delay = int(request.GET.get("hour_delay", 23))
        scheduled_for = timezone.now() + timedelta(hours=delay)
        new_reminder = ReminderSchedule.objects.create(
            schedule_time=scheduled_for, recipient_id=recipient_id, content=content
        )

        (
            ReminderSchedule.objects.filter(
                recipient_id=recipient_id, sent_time__isnull=True, cancelled=False
            )
            .exclude(pk=new_reminder.pk)
            .update(cancelled=True)
        )

        return Response({"accepted": True}, status=201)


class GetMsisdnTimezoneTurn(APIView):
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def update_profile(self, recipient_id, timezone):
        response = requests.patch(
            urljoin(settings.TURN_URL, f"/v1/contacts/{recipient_id}/profile"),
            data=json.dumps({"timezone": timezone}),
            headers={
                "Accept": "application/vnd.v1+json",
                "Authorization": "Bearer {}".format(settings.TURN_AUTH_TOKEN),
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()

    def post(self, request, *args, **kwargs):
        try:
            recipient_id = request.data["contacts"][0]["wa_id"]
        except KeyError:
            raise ValidationError(
                {"contacts": [{"wa_id": ["This field is required."]}]}
            )

        try:
            msisdn = phonenumbers.parse("+{}".format(recipient_id))
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError(
                {
                    "contacts": [
                        {
                            "wa_id": [
                                "This value must be a phone number with a region prefix."
                            ]
                        }
                    ]
                }
            )

        if not (
            phonenumbers.is_possible_number(msisdn)
            and phonenumbers.is_valid_number(msisdn)
        ):
            raise ValidationError(
                {
                    "contacts": [
                        {
                            "wa_id": [
                                "This value must be a phone number with a region prefix."
                            ]
                        }
                    ]
                }
            )

        zones = ph_timezone.time_zones_for_number(msisdn)
        if len(zones) == 1:
            approx_tz = zones[0]
        elif len(zones) > 1:
            approx_tz = get_middle_tz(zones)

        if request.query_params.get("save", "false").lower() == "true":
            self.update_profile(recipient_id, approx_tz)

        return Response({"success": True, "timezone": approx_tz}, status=200)


class GetMsisdnTimezones(APIView):
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        try:
            msisdn = request.data["msisdn"]
        except KeyError:
            raise ValidationError({"msisdn": ["This field is required."]})

        msisdn = msisdn if msisdn.startswith("+") else "+" + msisdn

        try:
            msisdn = phonenumbers.parse(msisdn)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError(
                {"msisdn": ["This value must be a phone number with a region prefix."]}
            )

        if not (
            phonenumbers.is_possible_number(msisdn)
            and phonenumbers.is_valid_number(msisdn)
        ):
            raise ValidationError(
                {"msisdn": ["This value must be a phone number with a region prefix."]}
            )

        zones = list(ph_timezone.time_zones_for_number(msisdn))

        if (
            len(zones) > 1
            and request.query_params.get("return_one", "false").lower() == "true"
        ):
            zones = [get_middle_tz(zones)]

        return Response({"success": True, "timezones": zones}, status=200)


class MaintenanceErrorResponse(APIView):
    def post(self, request, *args, **kwargs):
        try:
            recipient_id = request.data["contacts"][0]["wa_id"]
        except KeyError:
            status = 400
            message = {"contacts.0.wa_id": ["This field is required."]}
            return Response(message, status=status)

        content = (
            "*Maintenance update* ⚠️ \n\nWe are currently doing maintenance, "
            "with some features and messages being temporarily unavailable.\n\n"
            "We apologise for any inconvenience caused. Please try again later."
        )

        data = {
            "preview_url": False,
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "text",
            "text": {"body": content},
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(settings.TURN_AUTH_TOKEN),
        }

        s = requests.Session()
        response = s.post(
            url=urljoin(settings.TURN_URL, "/v1/messages"),
            data=json.dumps(data),
            headers=headers,
        )
        # Expecting a 200, raise for errors.
        response.raise_for_status()

        return Response({"accepted": True}, status=200)
