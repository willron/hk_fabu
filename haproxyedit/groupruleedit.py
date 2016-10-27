#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
by:willron
'''
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from haproxyedit.models import *
import json

def index(request, groupid):

    if 'LoginName' not in request.session:
        # 用户未登录跳转
        return HttpResponseRedirect('/login')

    if request.method == 'GET':

        LoginName = request.session['LoginName']
        allserver = HaproxyServer.objects.all()
        allgroup = HaproxyGroup.objects.all()
        group_with_server = {}
        for group in allgroup:
            ForeignKey_server = group.haproxyserver_set.all()
            group_with_server[group.GroupID] = ForeignKey_server


        return render(request, "groupruleedit.html", {'LoginName': LoginName,
                                                    'HaproxyServer': allserver,
                                                    'HaproxyGroup': allgroup,
                                                      'test': 'teaaast'
                                                    })
    else:
        # return render(request, "acl.html", {'test': 'good.good'})
        return HttpResponse(json.dumps({'falsemsg': 'falsefalse'}))