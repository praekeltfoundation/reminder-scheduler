import requests
from celery.exceptions import SoftTimeLimitExceeded
from requests.exceptions import RequestException
from urllib.parse import urljoin

from config.celery import app

from rapidpro_api.models import TurnRapidproConnection


def get_turn_field_value(connection, turn_field, msisdn):
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
    turn_value = turn_profile['fields'][turn_field]
    return turn_value

@app.task(
    autoretry_for=(RequestException, SoftTimeLimitExceeded),
    ignore_result=True,
    retry_backoff=True,
    max_retries=10,
    acks_late=True,
    soft_time_limit=10,
    time_limit=15,
)
def sync_profile_fields(connection_pk, rp_field, turn_field, msisdn):
    connection = TurnRapidproConnection.objects.get(pk=connection_pk)
    turn_value = get_turn_field_value(connection, turn_field, msisdn)

    rp_url = urljoin(
            connection.rp_url, f"/api/v2/contacts.json?urn=whatsapp:{msisdn}")
    rp_headers = {
        "Authorization": "Token {}".format(connection.rp_api_token)
    }
    if rp_field == "language":
        body = {rp_field: turn_value.lower()}
    else:
        body = {"fields": {rp_field: turn_value}}
    rp_response = requests.request(
        method="POST", url=rp_url, headers=rp_headers, json=body
    )
    rp_response.raise_for_status()
