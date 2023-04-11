import json

import responses
from responses.matchers import json_params_matcher
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rapidpro_api.models import TurnRapidproConnection
from rapidpro_api.tasks import get_turn_field_value
from quickreplies.tests import generate_hmac_signature

class RapidproApiViewTests(APITestCase):
    def test_hmac_missing(self):
        """
        If the HMAC secret is configured, and there's no HMAC header, or it's invalid,
        then we should return a 403
        """
        connection = TurnRapidproConnection.objects.create(
            description="test connection",
            hmac_secret="test-secret",
            rp_url="https://example.org",
            rp_api_token="some-token")
        url = reverse("profileSync-profileSync", args=[connection.pk])
        data = {"test": "body"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            url, data, format="json", HTTP_X_TURN_HOOK_SIGNATURE="invalid"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @responses.activate
    def test_profileSync_language_fields(self):
        """
        The view should retrieve the value of the Turn language field, convert to
        set the RapidPro language field to match the lowercase value
        """
        connection = TurnRapidproConnection.objects.create(
            description="test connection", turn_url="https://turn_example.org",
            turn_api_token="test-token", rp_api_token="some-token",
            rp_url="https://rp_example.org", hmac_secret="test-secret",
        )

        responses.add(
            method=responses.GET,
            url="https://turn_example.org/v1/contacts/16505551234/profile",
            json={"fields": {"language": "ENG"}}
        )

        expected_data = {"language": "eng"}
        responses.add(
            method=responses.POST,
            url="https://rp_example.org/api/v2/contacts.json?urn=whatsapp:16505551234",
            match=[json_params_matcher(expected_data)]
        )

        url = "{}?turn_field=language&rp_field=language".format(reverse(
            "profileSync-profileSync", args=[connection.pk]))
        data = {
            "contacts": [{
                "profile": {"name": "Example User"},
                "wa_id": "16505551234"
            }]
        }
        body = json.dumps(data, separators=(",", ":"))
        signature = generate_hmac_signature(body, connection.hmac_secret)
        response = self.client.post(
            url, data, format="json", HTTP_X_TURN_HOOK_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @responses.activate
    def test_profileSync_non_language_fields(self):
        """
        The view should retrieve the value of the Turn field and set the RapidPro
        field to match
        """
        connection = TurnRapidproConnection.objects.create(
            description="test connection", turn_url="https://turn_example.org",
            turn_api_token="test-token", rp_api_token="some-token",
            rp_url="https://rp_example.org", hmac_secret="test-secret",
        )
        turn_field = "test_turn_field"
        rp_field = "test_rp_field"

        responses.add(
            method=responses.GET,
            url="https://turn_example.org/v1/contacts/16505551234/profile",
            json={"fields": {turn_field: "turn_value"}}
        )

        expected_data = {"fields": {rp_field: "turn_value"}}
        responses.add(
            method=responses.POST,
            url="https://rp_example.org/api/v2/contacts.json?urn=whatsapp:16505551234",
            match=[json_params_matcher(expected_data)]
        )

        url = "{}?turn_field={}&rp_field={}".format(reverse(
            "profileSync-profileSync", args=[connection.pk]), turn_field, rp_field)
        data = {
            "contacts": [{
                "profile": {"name": "Example User"},
                "wa_id": "16505551234"
            }]
        }
        body = json.dumps(data, separators=(",", ":"))
        signature = generate_hmac_signature(body, connection.hmac_secret)
        response = self.client.post(
            url, data, format="json", HTTP_X_TURN_HOOK_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @responses.activate
    def test_profileSync_fails_if_turn_field_doesnt_exist(self):
        """
        turn_field should be a field that exists on the Turn profile
        """
        connection = TurnRapidproConnection.objects.create(
            description="test connection", turn_url="https://turn_example.org",
            turn_api_token="test-token", rp_api_token="some-token",
            rp_url="https://rp_example.org",
        )

        responses.add(
            method=responses.GET,
            url="https://turn_example.org/v1/contacts/16505551234/profile",
            json={"fields": {"existing_filed": "turn_value"}}
        )

        with self.assertRaises(KeyError):
            get_turn_field_value(connection, "not_existing_field", "16505551234")

    def test_profileSync_required_fields(self):
        """
        The rp_field, turn_field and msisdn should all be present in the request
        """
        connection = TurnRapidproConnection.objects.create(
            description="test connection", rp_api_token="some-token",
            rp_url="https://rp_example.org",
        )

        url = "{}?turn_field=language&rp_field=language".format(reverse(
            "profileSync-profileSync", args=[connection.pk]))
        response = self.client.post(
            url, {}, format="json"
        )
        self.assertEqual(
            response.data["contacts"][0]["wa_id"][0],
            "This field is required."
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = "{}?rp_field=language".format(reverse(
            "profileSync-profileSync", args=[connection.pk]))
        response = self.client.post(
            url, {}, format="json"
        )
        self.assertEqual(
            response.data["turn_field"], "This query parameter is required."
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = "{}?turn_field=language".format(reverse(
            "profileSync-profileSync", args=[connection.pk]))
        response = self.client.post(
            url, {}, format="json"
        )
        self.assertEqual(
            response.data["rp_field"], "This query parameter is required."
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
