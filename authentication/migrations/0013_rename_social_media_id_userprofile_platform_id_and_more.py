# Generated by Django 4.2.6 on 2023-10-27 04:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_alter_userprofile_profile_pic'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='social_media_id',
            new_name='platform_id',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='social_media_type',
            new_name='platform_type',
        ),
    ]
