from django.db import models
from django.contrib.auth.models import User
from boss_admin.models import EmployeeMaster, RegistersMaster, RegistersRoleMaster

class Notification(models.Model):
    SENT = 'Sent'
    RECEIVED = 'Received'
    APPROVED = 'Approved'

    CHOICES = {
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
        (APPROVED, 'Approved')
    }

    to_user = models.ForeignKey(EmployeeMaster, to_field="emp_id", related_name='notifications', on_delete=models.CASCADE, null=True)
    register_role = models.ForeignKey(RegistersRoleMaster, on_delete=models.CASCADE, null=True)
    notification_type = models.CharField(max_length=30, choices=CHOICES)
    is_read = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    registers_id = models.ForeignKey(RegistersMaster, on_delete=models.CASCADE, null=True)
    register_type = models.CharField(max_length=100, null=True)
    model_name = models.CharField(max_length=100, null=True)
    extra_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hyper_link = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(EmployeeMaster, to_field="emp_id", related_name='creatednotifications', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
