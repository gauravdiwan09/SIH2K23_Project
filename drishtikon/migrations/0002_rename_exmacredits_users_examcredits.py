# Generated by Django 4.2.6 on 2023-12-13 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drishtikon', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='users',
            old_name='exmacredits',
            new_name='examcredits',
        ),
    ]