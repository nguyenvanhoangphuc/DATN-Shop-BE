from django.db import models
from django.utils.translation import gettext_lazy as _
from app.models import StatusEnum

# ==========================
# CATEGORY MODEL
# ==========================
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    def __str__(self):
        return self.name


# ==========================
# MATERIAL MODEL
# ==========================
class Material(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, null=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)


    def __str__(self):
        return self.name


# ==========================
# BRAND MODEL
# ==========================
class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, null=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    def __str__(self):
        return self.name


# ==========================
# PRODUCT MODEL
# ==========================
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, null=True)
    detail_description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="products")
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name="products")
    image_url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)

    def __str__(self):
        return self.name


# ==========================
# SUBPRODUCT MODEL
# ==========================
class SubProduct(models.Model):
    id = models.AutoField(primary_key=True)
    color = models.CharField(max_length=50, null=False)
    size = models.CharField(max_length=20, null=False)
    old_price = models.BigIntegerField(null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    price = models.BigIntegerField(null=False)
    stock = models.IntegerField(default=0, null=False)
    image_url = models.TextField(blank=True, null=True)
    # saled_per_month	INT NOT NULL DEFAULT 0	Số lượng sản phẩm đã bán mỗi tháng
    saled_per_month = models.IntegerField(default=0, null=False)  # Số lượng sản phẩm đã bán mỗi tháng
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)


    def __str__(self):
        return f"{self.color} - {self.size}"


# ==========================
# PRODUCT-SUBPRODUCT MODEL
# ==========================
class ProductSubProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sub_products")
    sub_product = models.ForeignKey(SubProduct, on_delete=models.CASCADE, related_name="products")
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)
    class Meta:
        unique_together = ('product', 'sub_product')

    def __str__(self):
        return f"{self.product.name} - {self.sub_product.color} ({self.sub_product.size})"


# ==========================
# ORDER STATUS ENUM
# ==========================
class OrderStatus(models.TextChoices):
    PENDING = 'pending', _("Pending - Order created but not paid")
    PROCESSING = 'processing', _("Processing - Order paid and being prepared")
    SHIPPED = 'shipped', _("Shipped - Order sent to shipping company")
    DELIVERED = 'delivered', _("Delivered - Order successfully delivered")
    CANCELED = 'canceled', _("Canceled - Order canceled by user or system")
    REFUNDED = 'refunded', _("Refunded - Order refunded")
    FAILED = 'failed', _("Failed - Payment failed")
    RETURNED = 'returned', _("Returned - Order returned by customer")

