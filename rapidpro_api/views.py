import json
import requests

from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from urllib.parse import urljoin

from rapidpro_api.models import TurnRapidproConnection
from quickreplies.views import validate_hmac_signature


class ProfileSyncViewSet(GenericViewSet):
    queryset = TurnRapidproConnection.objects.all()
    serializer_class = Serializer

    @action(detail=True, methods=["POST"])
    def profileSync(self, request, pk=None):
        connection = self.get_object()
        validate_hmac_signature(
            connection.hmac_secret,
            request.META.get("HTTP_X_TURN_HOOK_SIGNATURE"),
            request.body,
        )

        rp_field = self.request.query_params.get('rp_field')
        if not rp_field:
            raise ValidationError({'rp_field': 'This query parameter is required.'})
        turn_field = self.request.query_params.get('turn_field')
        if not turn_field:
            raise ValidationError({'turn_field': 'This query parameter is required.'})
        try:
            msisdn = request.data['contacts'][0]['wa_id']
        except KeyError:
            raise ValidationError({"contacts":[{"wa_id": ["This field is required."]}]})

        turn_value = self.get_turn_field_value(turn_field, msisdn)

        rp_url = urljoin(
                connection.rp_url, f"/api/v2/contacts.json?urn=whatsapp:{msisdn}")
        rp_headers = {
            "Content-Type": "application/json",
            "Authorization": "Token {}".format(connection.rp_api_token)
        }
        if rp_field == "language":
            body = {rp_field: turn_value.lower()}
        else:
            body = {"fields": {rp_field: turn_value}}
        rp_response = requests.request(
            method="POST", url=rp_url, headers=rp_headers, data=json.dumps(body)
        )
        rp_response.raise_for_status()

        return Response()

    def get_turn_field_value(self, turn_field, msisdn):
        connection = self.get_object()
        turn_url = urljoin(
            connection.turn_url, f"/v1/contacts/{msisdn}/profile")
        turn_headers = {
            "Accept": "application/vnd.v1+json",
            "Authorization": "Bearer {}".format(connection.turn_api_token)
        }
        turn_response = requests.request(
            method="GET", url=turn_url, headers=turn_headers
        )
        turn_response.raise_for_status()

        turn_profile = turn_response.json()
        try:
            turn_value = turn_profile['fields'][turn_field]
        except (KeyError, AttributeError):
            raise ValidationError({'turn_field': 'Key not found in profile.'})
        return turn_value
