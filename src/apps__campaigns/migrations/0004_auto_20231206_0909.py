# Generated by Django 3.1.14 on 2023-12-06 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps__campaigns', '0003_campaigntechnologytestimonial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaigntechnologytestimonial',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apps__campaigns.campaign'),
        ),
    ]
