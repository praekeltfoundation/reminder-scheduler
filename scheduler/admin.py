from django.contrib import admin

from .models import ReminderSchedule, ReminderContent

admin.site.register(ReminderSchedule)
admin.site.register(ReminderContent)
