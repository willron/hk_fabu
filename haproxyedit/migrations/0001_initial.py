# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-01 08:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ACLRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ACLRuleID', models.CharField(max_length=40, unique=True)),
                ('CreateTime', models.DateTimeField(auto_now_add=True)),
                ('UpdateTime', models.DateTimeField(auto_now=True)),
                ('ACLName', models.CharField(max_length=40, unique=True)),
                ('ACLCriterion', models.CharField(max_length=40)),
                ('ACLFlags', models.CharField(max_length=40)),
                ('ACLOperator', models.CharField(blank=True, max_length=40, null=True)),
                ('ACLValue', models.CharField(max_length=40)),
                ('Comment', models.CharField(blank=True, max_length=900, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ACLRuleJudgeInActionRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Inverse', models.BooleanField(default=False)),
                ('Or', models.BooleanField(default=False)),
                ('ACLRuleID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='haproxyedit.ACLRule')),
            ],
        ),
        migrations.CreateModel(
            name='ActionRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ActionRuleID', models.CharField(max_length=40, unique=True)),
                ('CreateTime', models.DateTimeField(auto_now_add=True)),
                ('UpdateTime', models.DateTimeField(auto_now=True)),
                ('ActionMode', models.CharField(default='use_backend', max_length=40)),
                ('Judge', models.CharField(default='if', max_length=10)),
                ('Condition', models.CharField(blank=True, max_length=200, null=True)),
                ('Comment', models.CharField(blank=True, max_length=900, null=True)),
                ('ACLRuleID', models.ManyToManyField(to='haproxyedit.ACLRule')),
            ],
        ),
        migrations.CreateModel(
            name='BoolInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('WaitForCreateAnsibleHostsFile', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='HaproxyGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CreateTime', models.DateTimeField(auto_now_add=True)),
                ('UpdateTime', models.DateTimeField(auto_now=True)),
                ('GroupID', models.CharField(max_length=40, unique=True)),
                ('GroupName', models.CharField(max_length=40, unique=True)),
                ('GroupDisplayName', models.CharField(max_length=40)),
                ('ServerConfigFilePath', models.CharField(max_length=200)),
                ('GroupComment', models.CharField(blank=True, max_length=900, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HaproxyServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CreateTime', models.DateTimeField(auto_now_add=True)),
                ('UpdateTime', models.DateTimeField(auto_now=True)),
                ('ServerID', models.CharField(max_length=40, unique=True)),
                ('ServerIP', models.GenericIPAddressField(unique=True)),
                ('ServerComment', models.CharField(blank=True, max_length=900, null=True)),
                ('GroupID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='haproxyedit.HaproxyGroup')),
            ],
        ),
        migrations.CreateModel(
            name='WebBackendCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('BackendID', models.CharField(max_length=40, unique=True)),
                ('BackendClusterName', models.CharField(max_length=40, unique=True)),
                ('BackendServersList', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='actionrule',
            name='BackendID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='haproxyedit.WebBackendCluster'),
        ),
        migrations.AddField(
            model_name='actionrule',
            name='GroupID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='haproxyedit.HaproxyGroup'),
        ),
        migrations.AddField(
            model_name='aclrulejudgeinactionrule',
            name='ActionRuleID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='haproxyedit.ActionRule'),
        ),
    ]
