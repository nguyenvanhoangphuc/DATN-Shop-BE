from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# ==========================
# REVIEW MODEL
# ==========================
class Review(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reviews")
    sub_product = models.ForeignKey("products.SubProduct", on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id} - {self.sub_product} - {self.rating}⭐"
