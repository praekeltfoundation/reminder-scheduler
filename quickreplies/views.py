import base64
import hmac
from hashlib import sha256

from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from quickreplies.models import QuickReply


def validate_hmac_signature(secret, signature, body):
    if not secret:
        return
    if not signature:
        raise NotAuthenticated("No HMAC signature")

    h = hmac.new(secret.encode(), body, sha256)

    if not hmac.compare_digest(base64.b64encode(h.digest()).decode(), signature):
        raise AuthenticationFailed("Invalid HMAC signature")


class QuickReplyViewSet(GenericViewSet):
    queryset = QuickReply.objects.all()

    @action(detail=True, methods=["POST"])
    def message(self, request, pk=None):
        quickreply = self.get_object()
        validate_hmac_signature(
            quickreply.hmac_secret,
            request.META.get("HTTP_X_TURN_HOOK_SIGNATURE"),
            request.body,
        )
        return Response()
