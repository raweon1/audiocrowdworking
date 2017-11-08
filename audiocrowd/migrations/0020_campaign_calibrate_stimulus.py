# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-07 13:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('audiocrowd', '0019_auto_20171107_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='calibrate_stimulus',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='audiocrowd.Stimuli'),
            preserve_default=False,
        ),
    ]