# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-31 13:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('audiocrowd', '0008_worker_qualification_done'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='access_acr',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='worker',
            name='birth_year',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='worker',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='male', max_length=6),
        ),
        migrations.AlterField(
            model_name='worker',
            name='speech_test',
            field=models.IntegerField(choices=[(1, '1 Month'), (2, '3 Months'), (3, '6 Months'), (4, '9 Months'), (5, '1 year or more')], default=1),
        ),
        migrations.AlterField(
            model_name='worker',
            name='subjective_test',
            field=models.IntegerField(choices=[(1, '1 Month'), (2, '3 Months'), (3, '6 Months'), (4, '9 Months'), (5, '1 year or more')], default=1),
        ),
        migrations.AlterField(
            model_name='worker',
            name='volume',
            field=models.IntegerField(default=0),
        ),
    ]
