# Generated by Django 4.1.3 on 2022-11-14 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writingapp', '0003_alter_editormodel_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='editormodel',
            name='created_at',
            field=models.CharField(default='2022-11-14 16:52:40', max_length=100),
        ),
        migrations.AlterField(
            model_name='editormodel',
            name='modified_at',
            field=models.CharField(default='2022-11-14 16:52:40', max_length=100),
        ),
        migrations.AlterField(
            model_name='writingmodel',
            name='created_at',
            field=models.CharField(default='2022-11-14 16:52:40', max_length=100),
        ),
        migrations.AlterField(
            model_name='writingmodel',
            name='modified_at',
            field=models.CharField(default='2022-11-14 16:52:40', max_length=100),
        ),
        migrations.AlterField(
            model_name='writingmodel',
            name='participated_at',
            field=models.CharField(default='2022-11-14 16:52:40', max_length=100),
        ),
        migrations.AlterField(
            model_name='writingroommodel',
            name='created_at',
            field=models.CharField(default='2022-11-14 16:52:40', max_length=100),
        ),
    ]