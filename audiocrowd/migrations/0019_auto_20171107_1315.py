# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-07 12:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audiocrowd', '0018_auto_20171107_1155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configuration',
            name='stimuli_per_job',
        ),
        migrations.AddField(
            model_name='campaign',
            name='gold_standard_per_job',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='campaign',
            name='stimuli_per_job',
            field=models.IntegerField(default=10),
        ),
    ]
