from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

User = get_user_model()

class Role(models.TextChoices):
    STAFF = 'staff', 'Staff'
    APPROVER_L1 = 'approver_l1', 'Approver Level 1'
    APPROVER_L2 = 'approver_l2', 'Approver Level 2'
    FINANCE = 'finance', 'Finance'
    ADMIN = 'admin', 'Admin'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STAFF)

    def __str__(self):
        return f"{self.user.email if self.user.email else self.user.username} ({self.role})"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

