# Generated by Django 4.2.6 on 2023-12-15 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drishtikon', '0012_alter_studenttestinfo_time_left'),
    ]

    operations = [
        migrations.CreateModel(
            name='proctoring_log',
            fields=[
                ('pid', models.BigAutoField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('test_id', models.CharField(max_length=100)),
                ('voice_db', models.IntegerField(blank=True, default=0, null=True)),
                ('img_log', models.TextField()),
                ('user_movements_updown', models.SmallIntegerField()),
                ('user_movements_lr', models.SmallIntegerField()),
                ('user_movements_eyes', models.SmallIntegerField()),
                ('phone_detection', models.SmallIntegerField()),
                ('person_status', models.SmallIntegerField()),
                ('log_time', models.DateTimeField(auto_now_add=True)),
                ('uid', models.BigIntegerField()),
            ],
        ),
    ]