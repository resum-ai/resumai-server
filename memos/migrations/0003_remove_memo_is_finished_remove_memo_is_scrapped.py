# Generated by Django 5.0.3 on 2024-04-02 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("memos", "0002_memo_is_finished_memo_is_scrapped"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="memo",
            name="is_finished",
        ),
        migrations.RemoveField(
            model_name="memo",
            name="is_scrapped",
        ),
    ]
