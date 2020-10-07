from django.contrib import admin

from .models import ReminderSchedule, ReminderContent

@admin.register(ReminderSchedule)
class ContactImportAdmin(admin.ModelAdmin):
    list_display = ("recipient_id", "schedule_time", "sent_time", "cancelled")

admin.site.register(ReminderContent)
