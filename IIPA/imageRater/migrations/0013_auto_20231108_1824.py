# Generated by Django 4.2.7 on 2023-11-08 23:24

import uuid
from django.db import migrations, models


def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model("imageRater", "ImageRating")
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=["uuid"])


class Migration(migrations.Migration):
    dependencies = [
        ("imageRater", "0012_imagerating_uuid"),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]