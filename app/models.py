from django.db import models

# Create your models here.
class StatusEnum(models.IntegerChoices):
    ACTIVE = 0, 'Active'
    DELETED = 1, 'Deleted'