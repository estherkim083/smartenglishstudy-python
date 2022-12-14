# Generated by Django 4.1.3 on 2022-11-15 00:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mypage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myprofileinfomodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_profile_info_model', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatmodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_model_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
