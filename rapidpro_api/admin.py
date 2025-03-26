from django.contrib import admin

from rapidpro_api.models import TurnRapidproConnection


@admin.register(TurnRapidproConnection)
class TurnRapidproConnectionAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "rp_url", "turn_url")
