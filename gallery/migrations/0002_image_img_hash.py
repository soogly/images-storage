# Generated by Django 3.0 on 2020-04-17 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='img_hash',
            field=models.CharField(max_length=250, null=True, unique=True, verbose_name='hash of image file'),
        ),
    ]
