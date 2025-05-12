from django.db import models
from django.contrib.auth.models import User  # Import User mặc định của Django

# ==========================
# WISHLIST MODEL
# ==========================
class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    sub_product = models.ForeignKey('products.SubProduct', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'sub_product')

    def __str__(self):
        return f"{self.user.username} - {self.sub_product.id}"
