# Generated by Django 4.2.5 on 2023-09-16 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_userprofile_login_type_userprofile_social_media_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='passcode',
            field=models.CharField(max_length=20),
        ),
    ]
