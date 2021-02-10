from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from quickreplies.models import QuickReply


class QuickReplyViewTests(APITestCase):
    def test_hmac_missing(self):
        """
        If the HMAC secret is configured, and there's no HMAC header, or it's invalid,
        then we should return a 401
        """
        quickreply = QuickReply.objects.create(hmac_secret="test-secret")
        url = reverse("quickreply-message", args=[quickreply.pk])
        data = {"test": "body"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            url, data, format="json", HTTP_X_TURN_HOOK_SIGNATURE="invalid"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
