# Generated by Django 5.0.3 on 2024-04-21 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resume", "0006_chathistory_query_chathistory_response"),
    ]

    operations = [
        migrations.AddField(
            model_name="resume",
            name="company",
            field=models.CharField(default="네이버", max_length=255),
            preserve_default=False,
        ),
    ]
