import hmac
import json

from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from quickreplies.models import QuickReplyDestination
from quickreplies.tasks import http_request
from quickreplies.utils import generate_hmac_signature


def validate_hmac_signature(secret, signature, body):
    if not secret:
        return
    if not hmac.compare_digest(
        generate_hmac_signature(body.decode(), secret), signature or ""
    ):
        raise AuthenticationFailed("Invalid HMAC signature")


class QuickReplyViewSet(GenericViewSet):
    queryset = QuickReplyDestination.objects.all()
    serializer_class = Serializer

    @action(detail=True, methods=["POST"])
    def message(self, request, pk=None):
        quickreply = self.get_object()
        validate_hmac_signature(
            quickreply.hmac_secret,
            request.META.get("HTTP_X_TURN_HOOK_SIGNATURE"),
            request.body,
        )
        for msg in request.data.get("messages", []):
            if msg.get("type") == "button":
                msg["type"] = "text"
                button = msg.pop("button")
                msg["text"] = {"body": button["text"]}

        body = json.dumps(request.data, separators=(",", ":"))
        http_request.delay(
            method="POST",
            url=quickreply.url,
            headers={
                "X-Turn-Hook-Signature": generate_hmac_signature(
                    body, quickreply.hmac_secret
                ),
                "Content-Type": "application/json",
            },
            body=body,
        )
        return Response()
