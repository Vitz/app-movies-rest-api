# Generated by Django 2.0.3 on 2019-10-29 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_remove_movies_rating_avg'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movies',
            name='rating_amount',
        ),
        migrations.AddField(
            model_name='movies',
            name='ratingamount',
            field=models.IntegerField(null=True),
        ),
    ]
