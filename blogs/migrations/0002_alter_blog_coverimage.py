# Generated by Django 5.1.5 on 2025-01-29 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='coverimage',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
