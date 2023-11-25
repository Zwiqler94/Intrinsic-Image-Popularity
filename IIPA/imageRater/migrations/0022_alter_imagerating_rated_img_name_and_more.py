# Generated by Django 4.2.7 on 2023-11-20 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageRater', '0021_remove_imagerating_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagerating',
            name='rated_img_name',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='imagerating',
            name='rated_value',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='imagerating',
            name='url',
            field=models.URLField(),
        ),
    ]
