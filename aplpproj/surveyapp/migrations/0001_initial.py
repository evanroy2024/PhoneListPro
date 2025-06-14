# Generated by Django 5.1.7 on 2025-04-20 12:49

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('plpapp', '0004_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('survey_date', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('survey_token', models.CharField(max_length=15)),
                ('contacts', models.ManyToManyField(related_name='surveys', to='plpapp.usercontactlist')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to=settings.AUTH_USER_MODEL)),
                ('polltaker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to='plpapp.poltaker')),
                ('questions', models.ManyToManyField(related_name='surveys', to='plpapp.question')),
            ],
        ),
        migrations.CreateModel(
            name='SurveyResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('responses', models.JSONField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('completed', models.BooleanField(default=True)),
                ('denial_reason', models.TextField(blank=True, null=True)),
                ('contact', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='plpapp.usercontactlist')),
                ('polltaker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plpapp.poltaker')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveyapp.survey')),
            ],
        ),
    ]
