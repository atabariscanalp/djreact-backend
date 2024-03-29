# Generated by Django 3.0.7 on 2020-07-07 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import posts.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to=posts.models.upload_location)),
                ('title', models.TextField(blank=True, max_length=30, null=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('star_rate', models.FloatField(default=0.0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
