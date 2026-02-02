from django.db import models
from django.conf import settings


class ActivityLog(models.Model):
    """Simple admin activity log to show recent admin actions (logins/edits).

    This is a lightweight model used by the dashboard to surface admin activity.
    We keep it small to avoid interfering with existing project models.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} — {self.user} — {self.action}"
