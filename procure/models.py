from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from cloudinary_storage.storage import RawMediaCloudinaryStorage

User = get_user_model()

class PurchaseRequest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    vendor = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    proforma = models.FileField(upload_to='proformas/', null=True, blank=True)
    purchase_order = models.FileField(upload_to='pos/', null=True, blank=True)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True, storage=RawMediaCloudinaryStorage())

    last_approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    def __str__(self):
        return f"PR#{self.id} {self.title} [{self.status}]"

class RequestItem(models.Model):
    request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def total_price(self):
        return self.qty * self.unit_price

class Approval(models.Model):
    request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField()
    approved = models.BooleanField(null=True)  # None: pending, True: approved, False: rejected
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('request', 'approver', 'level'),)

class PurchaseOrder(models.Model):
    request = models.OneToOneField(PurchaseRequest, on_delete=models.CASCADE, related_name='po_obj')
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.JSONField()
    file = models.FileField(upload_to='generated_pos/', null=True, blank=True, storage=RawMediaCloudinaryStorage())

class ReceiptValidation(models.Model):
    request = models.OneToOneField(PurchaseRequest, on_delete=models.CASCADE, related_name='receipt_validation')
    validated_at = models.DateTimeField(null=True, blank=True)
    validation_result = models.JSONField(null=True, blank=True)
    discrepancies = models.JSONField(null=True, blank=True)
    is_valid = models.BooleanField(default=False)
