from django.db import models
from django.contrib.auth.models import User

class Vendor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_account'
    )
    bank_details = models.TextField()
    nid_number = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False) 

    is_approved = models.BooleanField(default=False)  # 🔥 NEW

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"Vendor: {self.user.username} ({status})"
