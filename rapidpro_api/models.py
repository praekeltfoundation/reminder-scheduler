from django.db import models
# from temba_client.v2 import TembaClient


class TurnRapidproConnection(models.Model):
    description = models.CharField(max_length=255)
    rp_url = models.URLField()
    rp_api_token = models.CharField(max_length=255)
    turn_url = models.URLField(blank=True)
    turn_api_token = models.CharField(max_length=1000, blank=True)
    hmac_secret = models.CharField(max_length=255, blank=True)

    # def get_rapidpro_client(self):
    #     return TembaClient(self.url, self.token)
