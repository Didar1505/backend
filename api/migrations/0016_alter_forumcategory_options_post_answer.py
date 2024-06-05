# Generated by Django 5.0.3 on 2024-06-04 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_forumcategory_alter_thread_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='forumcategory',
            options={'ordering': ['title'], 'verbose_name_plural': 'Forum-Categories'},
        ),
        migrations.AddField(
            model_name='post',
            name='answer',
            field=models.BooleanField(default=False),
        ),
    ]
