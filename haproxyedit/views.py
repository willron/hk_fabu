#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.db import IntegrityError
from haproxyedit.models import *
import json
import hashlib
import uuid
import re


RE_IP = re.compile(r'((([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))\.){3}(([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))')


def UUID_TO_MD5_CharField(tbname=None):

    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    uuidtomd5 = m.hexdigest()

    if tbname:
        return tbname + '_' + uuidtomd5
    else:
        return uuidtomd5


def check_ip_and_separate_operation(postdate):
    unprocess = postdate
    processed = {}
    processed['target'] = {}
    for k, v in unprocess.items():
        if k != 'csrfmiddlewaretoken':
            t = k.split('_')
            # print k,v,t
            processed['table'] = t[0]
            processed['operation'] = t[1]
            if k.endswith('ID'):
                processed['target']['id'] = v.strip()
            if k.endswith('IP'):
                processed['target']['ip'] = v.strip()
            if k.endswith('Comment'):
                processed['target']['comment'] = v.strip()
            if k.endswith('ConfigFilePath'):
                processed['target']['configfilepath'] = v.strip() if v != '' else '/usr/local/haproxy/etc/haproxy.cfg'
            if k.endswith('GroupName'):
                processed['target']['groupname'] = v.strip()
            if k.endswith('GroupDisplayName'):
                processed['target']['groupdisplayname'] = v.strip()

    print processed
    if 'ip' in processed['target']:
        checkip = RE_IP.match(processed['target']['ip'])
        if not checkip:
            return

    return processed


def haproxyedit(request):

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


        return render(request, "haproxyedit.html", {'LoginName': LoginName,
                                                    'HaproxyServer': allserver,
                                                    'HaproxyGroup': allgroup
                                                    })
    else:
        postdata = request.POST
        print postdata
        goodpostdata = check_ip_and_separate_operation(postdata)

        if not goodpostdata:
            result = {'state': 'false', 'msg': '无效IP！'}

        else:
            if goodpostdata['table'] == 'HG':
                # HaproxyGroup操作
                target = goodpostdata['target']
                result = {'state': 'success'}

                if goodpostdata['operation'] == 'Add':
                    if '' in target.values():
                        result = {'state': 'false', 'msg': '参数欠缺'}

                    elif not re.match(r'\w{1,20}', target['groupname']):
                        result = {'state': 'false', 'msg': '组名只能使用大小写字母数字与下划线'}

                    else:
                        try:
                            createdb = HaproxyGroup(GroupID=UUID_TO_MD5_CharField('HG'),
                                                    GroupName=target['groupname'],
                                                    GroupDisplayName=target['groupdisplayname'],
                                                    GroupComment=target['comment'],
                                                    ServerConfigFilePath=target['configfilepath'])
                            createdb.save()
                        except IntegrityError:
                            result = {'state': 'false', 'msg': '组名重复'}

                elif goodpostdata['operation'] == 'Modify':
                    pass

                elif goodpostdata['operation'] == 'Del':
                    pass

            elif goodpostdata['table'] == 'HS':
                # HaproxyServer操作
                target = goodpostdata['target']
                result = {'state': 'success'}

                if goodpostdata['operation'] == 'Add':
                    # 添加HaproxyServer
                    try:
                        createdb = HaproxyServer(ServerID=UUID_TO_MD5_CharField('HS'), ServerIP=target['ip'], ServerComment=target['comment'])
                        createdb.save()
                    except IntegrityError:
                        result = {'state': 'false', 'msg': '此IP已经存在！'}

                elif goodpostdata['operation'] == 'Del':
                    # 删除HaproxyServer
                    try:
                        HaproxyServer.objects.get(ServerID=target['id']).delete()
                    except HaproxyServer.DoesNotExist:
                        result = {'state': 'false', 'msg': '无效ID'}

                elif goodpostdata['operation'] == 'Modify':
                    # 修改HaproxyServer
                    try:
                        HaproxyServer.objects.filter(ServerID=target['id'])\
                            .update(ServerIP=target['ip'], ServerComment=target['comment'])
                    except HaproxyServer.DoesNotExist:
                        result = {'state': 'false', 'msg': '无效ID'}

        return HttpResponse(json.dumps(result))

