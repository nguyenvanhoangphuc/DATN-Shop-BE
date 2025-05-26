from django.db import models
from app.models import StatusEnum

# Create your models here.
# ==========================
# CART ITEM MODEL
# ==========================
class CartItem(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="cart_items")
    # sub_product = models.ForeignKey("SubProduct", on_delete=models.CASCADE, related_name="cart_items")
    sub_product = models.ForeignKey('products.SubProduct', on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    class Meta: 
        unique_together = ('user', 'sub_product')

    def __str__(self):
        return f"{self.quantity} x {self.sub_product} in {self.user.username}'s cart"
