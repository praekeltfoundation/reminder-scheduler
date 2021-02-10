from django.contrib import admin
from django.urls import reverse

from quickreplies.models import QuickReplyDestination


@admin.register(QuickReplyDestination)
class QuickReplyAdmin(admin.ModelAdmin):
    list_display = ("url", "hmac_secret")

    def view_on_site(self, obj):
        return reverse("quickreply-message", args=[obj.pk])
