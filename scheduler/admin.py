from django.contrib import admin

from .models import ReminderContent, ReminderSchedule


@admin.register(ReminderSchedule)
class ReminderScheduleAdmin(admin.ModelAdmin):
    list_display = ("recipient_id", "schedule_time", "sent_time", "cancelled")


admin.site.register(ReminderContent)
