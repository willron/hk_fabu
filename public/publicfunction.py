#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ConfigParser
from publicvar import *


def read_project_name(section=None):
    """
    从hosts文件中获取项目名
    :param section:项目名。如给定了项目名，则返回该项目的服务器列表
    :return:列表
    """
    # all_project_name = Project.objects.values_list('project_name', 'project_server')

    conf = ConfigParser.ConfigParser()
    conf.read(ansible_hosts)
    if section:
        return conf.options(section)
    return conf.sections()
