# Generated by Django 4.2.7 on 2023-11-20 05:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("imageRater", '0016_imagerating_created_at_imagerating_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name="imagerating",
            name="rating_obj",
            field=models.JSONField(default=dict),
        ),
    ]