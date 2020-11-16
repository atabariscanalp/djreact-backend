# Generated by Django 3.0.7 on 2020-09-20 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20200914_2354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(default='title', unique=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.TextField(default='title', max_length=30, unique=True, verbose_name='Title'),
        ),
    ]
