# Generated by Django 4.1.3 on 2022-11-14 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listeningapp', '0004_alter_listeningdatamodel_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listeningdatamodel',
            name='created_at',
            field=models.CharField(default='2022-11-14 16:52:40', max_length=100),
        ),
        migrations.AlterField(
            model_name='listeningdatamodel',
            name='modified_at',
            field=models.CharField(default='2022-11-14 16:52:40', max_length=100),
        ),
    ]