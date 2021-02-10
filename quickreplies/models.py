from django.db import models


class QuickReplyDestination(models.Model):
    url = models.URLField()
    hmac_secret = models.CharField(max_length=255, blank=True)
