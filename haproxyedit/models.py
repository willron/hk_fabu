#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class HaproxyGroup(models.Model):
    CreateTime = models.DateTimeField(auto_now_add=True)
    UpdateTime = models.DateTimeField(auto_now=True)
    GroupID = models.CharField(max_length=40, primary_key=True)
    GroupName = models.CharField(max_length=40, unique=True)
    GroupDisplayName = models.CharField(max_length=40)
    ServerConfigFilePath = models.CharField(max_length=200)
    GroupComment = models.CharField(max_length=900, blank=True, null=True)

    def __unicode__(self):
        return self.GroupDisplayName


class HaproxyServer(models.Model):
    CreateTime = models.DateTimeField(auto_now_add=True)
    UpdateTime = models.DateTimeField(auto_now=True)
    ServerID = models.CharField(max_length=40, primary_key=True)
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
# class ACLRule(models.Model):
#     ACLRuleID = models.CharField(max_length=40, primary_key=True)
#     ACLName = models.CharField(max_length=40)
#     GroupID = models.ForeignKey(HaproxyGroup, on_delete=models.CASCADE, null=True)
#     TCPForwardID = models.ForeignKey(TCPForward, on_delete=models.CASCADE, null=True)
#
#
# class BackenCluster(models.Model):
#     BackenID = models.CharField(max_length=40, primary_key=True)
#     BackenClusterName = models.CharField(max_length=40)
#     GroupID = models.ForeignKey(HaproxyGroup, on_delete=models.CASCADE)
#     TCPForwardID = models.ForeignKey(TCPForward, on_delete=models.CASCADE)
