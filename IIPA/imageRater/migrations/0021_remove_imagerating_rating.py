# Generated by Django 4.2.7 on 2023-11-20 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imageRater', '0020_auto_20231120_0146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagerating',
            name='rating',
        ),
    ]
