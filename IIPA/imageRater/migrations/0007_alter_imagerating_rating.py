# Generated by Django 4.2.6 on 2023-10-12 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageRater', '0006_alter_imagerating_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagerating',
            name='rating',
            field=models.JSONField(default=dict),
        ),
    ]