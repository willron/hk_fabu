#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from django.db import models


class Project(models.Model):
    project_name = models.CharField(max_length=60, primary_key=True)        # 项目模块名
    project_server = models.CharField(max_length=300)       # 项目模块部署的服务器IP列表
    project_msg = models.CharField(max_length=999, null=True)       # 项目模块说明
    project_port = models.IntegerField()
