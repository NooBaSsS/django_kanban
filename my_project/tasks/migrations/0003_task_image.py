# Generated by Django 5.1.2 on 2024-11-30 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_task_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='img/'),
        ),
    ]
