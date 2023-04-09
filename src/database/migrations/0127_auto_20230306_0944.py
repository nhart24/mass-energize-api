# Generated by Django 3.1.14 on 2023-03-06 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0126_auto_20221229_1337'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'ordering': ['-id', 'rank', 'title']},
        ),
        migrations.AlterModelOptions(
            name='useractionrel',
            options={'ordering': ('-id', 'status', 'user', 'action')},
        ),
        migrations.AddField(
            model_name='event',
            name='published_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
