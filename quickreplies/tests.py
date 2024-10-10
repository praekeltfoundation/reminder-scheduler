import base64
import hmac
import json
from hashlib import sha256

import responses
from django.urls import reverse
from responses.matchers import json_params_matcher
from rest_framework import status
from rest_framework.test import APITestCase

from quickreplies.models import QuickReplyDestination


def generate_hmac_signature(body: str, secret: str) -> str:
    h = hmac.new(secret.encode(), body.encode(), sha256)
    return base64.b64encode(h.digest()).decode()


class QuickReplyViewTests(APITestCase):
    def test_hmac_missing(self):
        """
        If the HMAC secret is configured, and there's no HMAC header, or it's invalid,
        then we should return a 401
        """
        quickreply = QuickReplyDestination.objects.create(hmac_secret="test-secret")
        url = reverse("quickreply-message", args=[quickreply.pk])
        data = {"test": "body"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            url, data, format="json", HTTP_X_TURN_HOOK_SIGNATURE="invalid"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @responses.activate
    def test_quickreply(self):
        """
        If the message is a quickreply, then it should be forwarded as a normal message
        to the configured URL
        """
        quickreply: QuickReplyDestination = QuickReplyDestination.objects.create(
            url="https://example.org", hmac_secret="test-secret"
        )
        url: str = reverse("quickreply-message", args=[quickreply.pk])
        data = {
            "messages": [
                {
                    "button": {"payload": "No-Button-Payload", "text": "No"},
                    "context": {
                        "from": "16315558007",
                        "id": "gBGGFmkiWVVPAgkgQkwi7IORac0",
                    },
                    "from": "16505551234",
                    "id": "ABGGFmkiWVVPAgo-sKD87hgxPHdF",
                    "timestamp": "1591210827",
                    "type": "button",
                }
            ]
        }
        body = json.dumps(data, separators=(",", ":"))
        signature = generate_hmac_signature(body, quickreply.hmac_secret)
        expected_data = {
            "messages": [
                {
                    "text": {"body": "No"},
                    "context": {
                        "from": "16315558007",
                        "id": "gBGGFmkiWVVPAgkgQkwi7IORac0",
                    },
                    "from": "16505551234",
                    "id": "ABGGFmkiWVVPAgo-sKD87hgxPHdF",
                    "timestamp": "1591210827",
                    "type": "text",
                }
            ]
        }

        responses.add(
            method=responses.POST,
            url="https://example.org",
            match=[json_params_matcher(expected_data)],
        )

        response = self.client.post(
            url, data, format="json", HTTP_X_TURN_HOOK_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        [call] = responses.calls
        self.assertEqual(
            call.request.headers["X-Turn-Hook-Signature"],
            generate_hmac_signature(call.request.body.decode(), quickreply.hmac_secret),
        )

    @responses.activate
    def test_non_quickreply(self):
        """
        If the message is not a quickreply, then it should be forwarded as is to the
        configured URL
        """
        quickreply: QuickReplyDestination = QuickReplyDestination.objects.create(
            url="https://example.org", hmac_secret="test-secret"
        )
        url: str = reverse("quickreply-message", args=[quickreply.pk])
        data = {
            "messages": [
                {
                    "text": {"body": "No"},
                    "from": "16505551234",
                    "id": "ABGGFmkiWVVPAgo-sKD87hgxPHdF",
                    "timestamp": "1591210827",
                    "type": "text",
                }
            ]
        }
        body = json.dumps(data, separators=(",", ":"))
        signature = generate_hmac_signature(body, quickreply.hmac_secret)

        responses.add(
            method=responses.POST,
            url="https://example.org",
            match=[json_params_matcher(data)],
        )

        response = self.client.post(
            url, data, format="json", HTTP_X_TURN_HOOK_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        [call] = responses.calls
        self.assertEqual(call.request.headers["X-Turn-Hook-Signature"], signature)
