# Generated by Django 4.2.1 on 2023-05-20 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="username",
        ),
    ]