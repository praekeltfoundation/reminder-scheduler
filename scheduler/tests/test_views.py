import json
import responses
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase
from requests.exceptions import HTTPError


class GetMsisdnTimezoneTurnTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            'adminuser', "admin_password")

    def test_login_required_to_get_timezones(self):
        response = self.client.post(
            "/scheduler/timezone/turn",
            json={'contacts': [{'msisdn': 'something'}]},
            content_type='application/json')

        self.assertEqual(response.status_code, 401)

    def test_unexpected_data_format_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezone/turn",
            data=json.dumps({'contacts': [{'msisdn': 'something'}]}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"contacts.0.wa_id": ["This field is required."]}
        )
        self.assertEqual(response.status_code, 400)

    def test_phonenumber_unparseable_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezone/turn",
            data=json.dumps({'contacts': [{'wa_id': 'something'}]}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"contacts.0.wa_id": ['This value must be a phone number with a region '
                                  'prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_not_possible_phonenumber_returns_400(self):
        # If the length of a number doesn't match accepted length for it's region
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezone/turn",
            data=json.dumps({'contacts': [{'wa_id': '120012301'}]}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"contacts.0.wa_id": ['This value must be a phone number with a region '
                                  'prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_phonenumber_returns_400(self):
        # If a phone number is invalid for it's region
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezone/turn",
            data=json.dumps({'contacts': [{'wa_id': '12001230101'}]}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"contacts.0.wa_id": ['This value must be a phone number with a region '
                                  'prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_single_timezone_number(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezone/turn",
            data=json.dumps({'contacts': [{'wa_id': '27345678910'}]}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"success": True, "timezone": "Africa/Johannesburg"}
        )
        self.assertEqual(response.status_code, 200)

    def test_multiple_timezone_number_returns_one(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezone/turn",
            data=json.dumps({'contacts': [{'wa_id': '61498765432'}]}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"success": True, "timezone": "Australia/Eucla"}
        )
        self.assertEqual(response.status_code, 200)

    @responses.activate
    @override_settings(TURN_URL='https://fake_turn.url')
    @override_settings(TURN_AUTH_TOKEN='fake-turn-token')
    def test_save_param_true_updates_turn_profile(self):
        self.client.force_authenticate(user=self.admin_user)

        responses.add(responses.PATCH,
            'https://fake_turn.url/v1/contacts/61498765432/profile',
            body=json.dumps({"version":"0.0.1-alpha", "fields":{"timezone":"Australia/Eucla"}}),
            match=[responses.json_params_matcher({"timezone": "Australia/Eucla"})])

        response = self.client.post(
            "/scheduler/timezone/turn?save=true",
            data=json.dumps({'contacts': [{'wa_id': '61498765432'}]}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"success": True, "timezone": "Australia/Eucla"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(responses.calls[0].request.headers['Authorization'],
            "Bearer fake-turn-token")

    @responses.activate
    @override_settings(TURN_URL='https://fake_turn.url')
    @override_settings(TURN_AUTH_TOKEN='fake-turn-token')
    def test_save_param_true_raises_error_if_patch_fails(self):
        self.client.force_authenticate(user=self.admin_user)

        responses.add(responses.PATCH,
            'https://fake_turn.url/v1/contacts/61498765432/profile',
            status=404,
            match=[responses.json_params_matcher({"timezone": "Australia/Eucla"})])

        with self.assertRaises(HTTPError):
            response = self.client.post(
                "/scheduler/timezone/turn?save=true",
                data=json.dumps({'contacts': [{'wa_id': '61498765432'}]}),
                content_type='application/json')

        self.assertEqual(responses.calls[0].request.headers['Authorization'],
            "Bearer fake-turn-token")


class GetMsisdnTimezonesTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            'adminuser', "admin_password")

    def test_auth_required_to_get_timezones(self):
        response = self.client.post(
            "/scheduler/timezone/turn",
            data={'contacts': [{'msisdn': 'something'}]},
            content_type='application/json')

        self.assertEqual(response.status_code, 401)

    def test_no_msisdn_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezones/",
            data=json.dumps({'contact': {'urn': 'something'}}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"msisdn": ["This field is required."]}
        )
        self.assertEqual(response.status_code, 400)

    def test_phonenumber_unparseable_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezones/",
            data=json.dumps({'msisdn': 'something'}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"msisdn": ['This value must be a phone number with a region prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_not_possible_phonenumber_returns_400(self):
        # If the length of a number doesn't match accepted length for it's region
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezones/",
            data=json.dumps({'msisdn': '120012301'}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"msisdn": ['This value must be a phone number with a region prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_phonenumber_returns_400(self):
        # If a phone number is invalid for it's region
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezones/",
            data=json.dumps({'msisdn': '12001230101'}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"msisdn": ['This value must be a phone number with a region prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_phonenumber_with_plus(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezones/",
            data=json.dumps({'msisdn': '+27345678910'}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"success": True, "timezones": ["Africa/Johannesburg"]}
        )
        self.assertEqual(response.status_code, 200)

    def test_single_timezone_number(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezones/",
            data=json.dumps({'msisdn': '27345678910'}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"success": True, "timezones": ["Africa/Johannesburg"]}
        )
        self.assertEqual(response.status_code, 200)

    def test_multiple_timezone_number_returns_all(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/scheduler/timezones/",
            data=json.dumps({'msisdn': '61498765432'}),
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"success": True, "timezones": [
                'Australia/Adelaide',
                'Australia/Eucla',
                'Australia/Lord_Howe',
                'Australia/Perth',
                'Australia/Sydney',
                'Indian/Christmas',
                'Indian/Cocos']}
        )
        self.assertEqual(response.status_code, 200)
