# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-03 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audiocrowd', '0016_ratingset_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='gold_standard_questions',
            field=models.ManyToManyField(to='audiocrowd.GoldStandardQuestions'),
        ),
    ]
