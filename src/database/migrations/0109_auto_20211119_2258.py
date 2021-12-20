# Generated by Django 3.1.13 on 2021-11-19 22:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0108_subscriber_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='visit_log',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.CreateModel(
            name='DeviceProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('ip_address', models.CharField(max_length=100, null=True)),
                ('device_type', models.CharField(max_length=100, null=True)),
                ('operating_system', models.CharField(max_length=100, null=True)),
                ('browser', models.CharField(max_length=100, null=True)),
                ('visit_log', models.JSONField(blank=True, default=dict, null=True)),
                ('is_deleted', models.BooleanField(blank=True, default=False)),
                ('location', models.ManyToManyField(blank=True, to='database.Location')),
                ('user_profiles', models.ManyToManyField(blank=True, to='database.UserProfile')),
            ],
        ),
    ]
