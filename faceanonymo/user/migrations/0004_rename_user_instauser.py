# Generated by Django 4.2.11 on 2024-04-18 19:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('user', '0003_user_is_active_user_is_staff_user_last_login_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='InstaUser',
        ),
    ]
