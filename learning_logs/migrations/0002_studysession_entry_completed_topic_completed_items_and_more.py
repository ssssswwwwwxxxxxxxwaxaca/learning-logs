# Generated by Django 5.1.7 on 2025-04-22 14:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learning_logs", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudySession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_time", models.DateTimeField(auto_now_add=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name="entry",
            name="completed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="topic",
            name="completed_items",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="topic",
            name="total_items",
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name="LearningGoal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("decription", models.TextField(blank=True)),
                ("target_date", models.DateField()),
                ("completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_goals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
