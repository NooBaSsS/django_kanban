# Generated by Django 5.1.2 on 2024-12-04 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_task_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='task/img/'),
        ),
    ]
