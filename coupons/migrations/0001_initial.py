# Generated by Django 5.1.6 on 2025-03-13 17:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('valid_from', models.DateTimeField()),
                ('valid_until', models.DateTimeField()),
            ],
        ),
    ]
