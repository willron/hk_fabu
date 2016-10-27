# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-24 02:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_name', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('project_server', models.CharField(max_length=300)),
                ('project_msg', models.CharField(max_length=999, null=True)),
                ('project_port', models.IntegerField()),
            ],
        ),
    ]