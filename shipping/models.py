from django.db import models
from django.utils.translation import gettext_lazy as _
from app.models import StatusEnum

# ==========================
# SHIPPING MODEL
# ==========================
class Shipping(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SHIPPED = "shipped", _("Shipped")
        IN_TRANSIT = "in_transit", _("In Transit")
        OUT_FOR_DELIVERY = "out_for_delivery", _("Out for Delivery")
        DELIVERED = "delivered", _("Delivered")

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="shippings")
    tracking_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"Shipping {self.id} - Order {self.order.id} - {self.status}"
