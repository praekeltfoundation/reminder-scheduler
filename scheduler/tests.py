from django.test import TestCase


class GetMsisdnTimezoneTurnTest(TestCase):
    def test_unexpected_data_format_returns_400(self):
        response = self.client.post(
            "/timezone/turn", data={'contacts':[{'msisdn':'something'}]},
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"contacts.0.wa_id": ["This field is required."]}
        )
        self.assertEqual(response.status_code, 400)

    def test_phonenumber_unparseable_returns_400(self):
        response = self.client.post(
            "/timezone/turn", data={'contacts':[{'wa_id':'something'}]},
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"contacts.0.wa_id": ['This value must be a phone number with a region '
                                  'prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_not_possible_phonenumber_returns_400(self):
        # If the length of a number doesn't match accepted length for it's region
        response = self.client.post(
            "/timezone/turn", data={'contacts':[{'wa_id':'120012301'}]},
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"contacts.0.wa_id": ['This value must be a phone number with a region '
                                  'prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_phonenumber_returns_400(self):
        # If a phone number is invalid for it's region
        response = self.client.post(
            "/timezone/turn", data={'contacts':[{'wa_id':'12001230101'}]},
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"contacts.0.wa_id": ['This value must be a phone number with a region '
                                  'prefix.']}
        )
        self.assertEqual(response.status_code, 400)

    def test_single_timezone_number(self):
        response = self.client.post(
            "/timezone/turn", data={'contacts':[{'wa_id':'27345678910'}]},
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"success": True, "timezone": "Africa/Johannesburg"}
        )
        self.assertEqual(response.status_code, 200)

    def test_single_timezone_number_returns_one(self):
        response = self.client.post(
            "/timezone/turn", data={'contacts':[{'wa_id':'61498765432'}]},
            content_type='application/json')

        self.assertEqual(
            response.data,
            {"success": True, "timezone": "Australia/Perth"}
        )
        self.assertEqual(response.status_code, 200)
