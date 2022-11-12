# Generated by Django 4.1.3 on 2022-11-12 22:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('listeningapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='listeningdatamodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listening_data_model', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='listeningblanksheetmodel',
            name='target_data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='listeningapp.listeningdatamodel'),
        ),
    ]
