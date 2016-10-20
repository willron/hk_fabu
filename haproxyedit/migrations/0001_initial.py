# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-19 01:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HaproxyGroup',
            fields=[
                ('CreateTime', models.DateTimeField(auto_now_add=True)),
                ('UpdateTime', models.DateTimeField(auto_now=True)),
                ('GroupID', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('GroupName', models.CharField(max_length=40, unique=True)),
                ('GroupDisplayName', models.CharField(max_length=40)),
                ('ServerConfigFilePath', models.CharField(max_length=200)),
                ('GroupComment', models.CharField(blank=True, max_length=900, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HaproxyServer',
            fields=[
                ('CreateTime', models.DateTimeField(auto_now_add=True)),
                ('UpdateTime', models.DateTimeField(auto_now=True)),
                ('ServerID', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('ServerIP', models.GenericIPAddressField(unique=True)),
                ('ServerComment', models.CharField(blank=True, max_length=900, null=True)),
                ('GroupID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='haproxyedit.HaproxyGroup')),
            ],
        ),
    ]