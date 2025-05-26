from django.db import models
from enum import Enum
from app.models import StatusEnum

class GenderEnum(models.IntegerChoices):
    MALE = 0, 'Male'
    FEMALE = 1, 'Female'

class User(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]
    
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.TextField()
    refresh_token = models.CharField(max_length=255, null= True, blank=True)
    image_url = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.IntegerField(choices=GenderEnum.choices, default=GenderEnum.MALE)
    address = models.TextField(blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    address_billing = models.TextField(blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    status_enum = models.IntegerField(choices=StatusEnum.choices, default=StatusEnum.ACTIVE)
    
    def __str__(self):
        return self.username