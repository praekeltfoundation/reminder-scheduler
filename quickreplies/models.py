from django.db import models


class QuickReply(models.Model):
    url = models.URLField()
    hmac_secret = models.CharField(max_length=255, blank=True)
