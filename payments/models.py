from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from app.models import StatusEnum

# ==========================
# PAYMENT METHOD MODEL
# ==========================
class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)
    description = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    def __str__(self):
        return self.name


# ==========================
# PAYMENT MODEL
# ==========================
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        FAILED = "failed", _("Failed")

    # order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="payments")
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payments")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name="payments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"Payment {self.id} - {self.order.id} - {self.status}"
