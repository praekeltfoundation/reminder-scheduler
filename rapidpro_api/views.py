from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from quickreplies.views import validate_hmac_signature
from rapidpro_api.models import TurnRapidproConnection
from rapidpro_api.tasks import sync_profile_fields


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

        rp_field = self.request.query_params.get("rp_field")
        if not rp_field:
            raise ValidationError({"rp_field": "This query parameter is required."})
        turn_field = self.request.query_params.get("turn_field")
        if not turn_field:
            raise ValidationError({"turn_field": "This query parameter is required."})
        try:
            msisdn = request.data["contacts"][0]["wa_id"]
        except KeyError:
            raise ValidationError(
                {"contacts": [{"wa_id": ["This field is required."]}]}
            )

        sync_profile_fields.delay(connection.pk, rp_field, turn_field, msisdn)

        return Response()
