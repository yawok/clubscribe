# Generated by Django 4.2.1 on 2023-05-24 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "main",
            "0006_rename_subscription_id_subscriptionplan_catalog_item_id_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="subscriptionplan",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="subscriptionplan",
            name="price",
            field=models.DecimalField(decimal_places=2, default=2, max_digits=4),
            preserve_default=False,
        ),
    ]
