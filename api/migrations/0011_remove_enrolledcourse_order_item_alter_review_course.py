# Generated by Django 5.0.3 on 2024-05-30 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_review_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrolledcourse',
            name='order_item',
        ),
        migrations.AlterField(
            model_name='review',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.course'),
        ),
    ]
