# Generated by Django 4.1.3 on 2022-11-14 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('readingapp', '0005_alter_readingdatamodel_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readingdatamodel',
            name='created_at',
            field=models.CharField(default='2022-11-14 16:53:25', max_length=100),
        ),
        migrations.AlterField(
            model_name='readingdatamodel',
            name='modified_at',
            field=models.CharField(default='2022-11-14 16:53:25', max_length=100),
        ),
    ]