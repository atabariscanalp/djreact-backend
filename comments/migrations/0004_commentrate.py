# Generated by Django 3.0.7 on 2020-09-21 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comments', '0003_comment_star_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.FloatField(default=0.0)),
                ('is_active', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='comments.Comment')),
                ('rater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commentRater', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
