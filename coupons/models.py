from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# ==========================
# COUPON MODEL
# ==========================
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}%"

    def is_valid(self):
        """Kiểm tra xem mã giảm giá có còn hiệu lực hay không"""
        from django.utils.timezone import now
        return self.valid_from <= now() <= self.valid_until and self.quantity > 0
