# Generated by Django 5.0.3 on 2024-05-24 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_cartorder_sub_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='type',
            field=models.CharField(blank=True, choices=[('Online', 'Online'), ('In-person', 'In-person')], default='Online', max_length=100, null=True),
        ),
    ]
