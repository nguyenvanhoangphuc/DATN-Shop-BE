from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from app.models import StatusEnum

# ==========================
# ORDER MODEL
# ==========================
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        SHIPPED = "shipped", _("Shipped")
        DELIVERED = "delivered", _("Delivered")
        CANCELED = "canceled", _("Canceled")
        REFUNDED = "refunded", _("Refunded")
        FAILED = "failed", _("Failed")
        RETURNED = "returned", _("Returned")

    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders")
    subtotal = models.BigIntegerField(null=False)
    tax = models.BigIntegerField(null=False)
    discount = models.BigIntegerField(null=False, default=0)
    shipping_cost = models.BigIntegerField(null=False)
    total_price = models.BigIntegerField(null=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"


# ==========================
# ORDER ITEM MODEL
# ==========================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    # sub_product = models.ForeignKey("SubProduct", on_delete=models.CASCADE, related_name="order_items")
    sub_product = models.ForeignKey("products.SubProduct", on_delete=models.CASCADE, related_name="order_items")
    quantity = models.IntegerField(default=1)
    price = models.BigIntegerField(null=False)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    def __str__(self):
        return f"{self.quantity} x {self.sub_product} in Order {self.order.id}"
