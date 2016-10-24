#!/usr/bin/env python
# -*- coding:utf-8 -*-


ANSILBE_HOSTS = '/etc/ansible/hosts.bak'        # ansible的hosts文件路径
ANSILBE_HAPROXYHOSTS = '/etc/ansible/haproxyhosts.bak'        # ansible的hosts文件路径
#ANSILBE_HOSTS = '/home/fabu/.ansible/hosts'        # ansible的hosts文件路径
#ANSILBE_HAPROXYHOSTS = '/home/fabu/.ansible/haproxyhosts'        # ansible的hosts文件路径
ANSIBLE_PLAYBOOK_PATH = '/home/fabu/ansible_playbook'
FABU_YML_PATH = ANSIBLE_PLAYBOOK_PATH + '/' + 'fabu.yml '     # 用于升级发布时的playbook文件路径
NEWFABU_YML_PATH = ANSIBLE_PLAYBOOK_PATH + '/' + 'newfabu.yml '       # 用于全新发布时的playbook文件路径
OPERATION_YML_PATH = ANSIBLE_PLAYBOOK_PATH + '/' + 'startstoprestart.yml'
THE_SSH_PORT = 9055
TOMCAT_LOG_PATH_MOUNT = '/tomcat_logs'
