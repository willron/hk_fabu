#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class HaproxyGroup(models.Model):
    CreateTime = models.DateTimeField(auto_now_add=True)
    UpdateTime = models.DateTimeField(auto_now=True)
    GroupID = models.CharField(max_length=40, unique=True)
    GroupName = models.CharField(max_length=40, unique=True)
    GroupDisplayName = models.CharField(max_length=40)
    ServerConfigFilePath = models.CharField(max_length=200)
    GroupComment = models.CharField(max_length=900, blank=True, null=True)

    def __unicode__(self):
        return self.GroupDisplayName


class HaproxyServer(models.Model):
    CreateTime = models.DateTimeField(auto_now_add=True)
    UpdateTime = models.DateTimeField(auto_now=True)
    ServerID = models.CharField(max_length=40, unique=True)
    ServerIP = models.GenericIPAddressField(unique=True)
    ServerComment = models.CharField(max_length=900, null=True, blank=True)
    GroupID = models.ForeignKey(HaproxyGroup, on_delete=models.SET_NULL, blank=True, null=True)

    def __unicode__(self):
        return self.ServerIP

class BoolInfo(models.Model):
    WaitForCreateAnsibleHostsFile = models.BooleanField()


# class TCPForward(models.Model):
#     TCPForwardID = models.CharField(max_length=40, primary_key=True)
#     TCPForwardName = models.CharField(max_length=40)
#     GroupID = models.ForeignKey(HaproxyGroup, on_delete=models.CASCADE)
#
#
class ACLRule(models.Model):
    ACLRuleID = models.CharField(max_length=40, unique=True)
    CreateTime = models.DateTimeField(auto_now_add=True)
    UpdateTime = models.DateTimeField(auto_now=True)
    ACLName = models.CharField(max_length=40, unique=True)
    ACLCriterion = models.CharField(max_length=40)
    ACLFlags = models.CharField(max_length=40)      # -i -m -f
    ACLOperator = models.CharField(max_length=40, null=True, blank=True)
    ACLValue = models.CharField(max_length=40)
    Comment = models.CharField(max_length=900, null=True, blank=True)

    def __unicode__(self):
        return self.ACLName


class WebBackendCluster(models.Model):
    BackendID = models.CharField(max_length=40, unique=True)
    CreateTime = models.DateTimeField(auto_now_add=True)    # 创建时间
    UpdateTime = models.DateTimeField(auto_now=True)    # 更新时间
    BackendClusterName = models.CharField(max_length=40, unique=True)
    BackendServersList = models.TextField()
    Comment = models.CharField(max_length=900, null=True, blank=True)

    def __unicode__(self):
        return self.BackendClusterName

    def serverslist_to_list(self):
        return self.BackendServersList.split(',')


class ActionRule(models.Model):
    ActionRuleID = models.CharField(max_length=40, unique=True)    # 唯一ID
    CreateTime = models.DateTimeField(auto_now_add=True)    # 创建时间
    UpdateTime = models.DateTimeField(auto_now=True)    # 更新时间
    GroupID = models.ForeignKey(HaproxyGroup, on_delete=models.CASCADE)  # 所属组的组ID
    ActionMode = models.CharField(max_length=40, default='use_backend')     # 操作模式
    BackendID = models.ForeignKey(WebBackendCluster, on_delete=models.CASCADE)      # 相关联的后端集群ID
    Judge = models.CharField(max_length=10, default='if')       # if/unless
    ACLRuleID = models.ManyToManyField(ACLRule)     # 相关联的ACL规则ID
    Condition = models.CharField(max_length=200, blank=True, null=True)     # 判断的条件。预留
    Comment = models.CharField(max_length=900, null=True, blank=True)       # 备注


class ACLRuleJudgeInActionRule(models.Model):
    CreateTime = models.DateTimeField(auto_now_add=True)    # 创建时间
    UpdateTime = models.DateTimeField(auto_now=True)    # 更新时间
    ACLRuleID = models.ForeignKey(ACLRule)
    ActionRuleID = models.ForeignKey(ActionRule)
    Inverse = models.BooleanField(default=False)     # 此ACL规则在Action规则中是否取反
    Or = models.BooleanField(default=False)      # 此ACL规则在Action规则中与其他ACL关系




