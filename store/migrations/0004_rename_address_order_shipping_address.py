# Generated by Django 5.1.4 on 2024-12-12 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_order_address_order_email_order_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='address',
            new_name='shipping_address',
        ),
    ]
