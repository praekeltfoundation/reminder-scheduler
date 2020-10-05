from django.db import models


class ReminderSchedule(models.Model):
    schedule_time = models.DateTimeField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_time = models.DateTimeField(null=True, blank=True)
    recipient_id = models.CharField(max_length=30, null=False, blank=False)
    content = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                name='sent_time',
                fields=['sent_time', 'schedule_time'],
                condition=models.Q(sent_time__isnull=True)),
        ]
