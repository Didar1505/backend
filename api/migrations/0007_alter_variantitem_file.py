# Generated by Django 5.0.3 on 2024-05-26 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_notification_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variantitem',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='course-file'),
        ),
    ]
