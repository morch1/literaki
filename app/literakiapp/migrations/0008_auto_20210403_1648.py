# Generated by Django 3.1.7 on 2021-04-03 14:48

from django.db import migrations, models
import literakiapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('literakiapp', '0007_auto_20210403_1501'),
    ]

    operations = [
        migrations.AddField(
            model_name='playeringame',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='game',
            name='letters',
            field=models.CharField(default=literakiapp.models.randletters, max_length=100),
        ),
    ]