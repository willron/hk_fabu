# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-26 12:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haproxyedit', '0003_auto_20161026_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boolinfo',
            name='WaitForCreateAnsibleHostsFile',
            field=models.BooleanField(),
        ),
    ]