# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-18 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_auto_20160914_0654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logging',
            name='log_date',
            field=models.CharField(max_length=99999),
        ),
    ]
