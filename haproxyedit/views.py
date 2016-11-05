#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.db import IntegrityError
from haproxyedit.models import *
from public.publicvar import ANSILBE_HAPROXYHOSTS, THE_SSH_PORT
import json
import hashlib
import uuid
import re


RE_IP = re.compile(r'^((([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))\.){3}(([1-9]?|1\d)\d|2([0-4]\d|5[0-5]))$')


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
            processed['table'] = t[0]
            processed['operation'] = t[1]
            if k.endswith('ID'):
                processed['target']['id'] = v.strip()
            if k.endswith('IP'):
                processed['target']['ip'] = v.strip()
            if k.endswith('Comment'):
                processed['target']['comment'] = v.strip() if v != '' else '无'
            if k.endswith('ConfigFilePath'):
                processed['target']['configfilepath'] = v.strip() if v != '' else '/usr/local/haproxy/etc/haproxy.cfg'
            if k.endswith('GroupName'):
                processed['target']['groupname'] = v.strip()
            if k.endswith('GroupDisplayName'):
                processed['target']['groupdisplayname'] = v.strip()


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

        if 'groupid' in request.GET:
            groupid = request.GET['groupid']

            bindedserver = HaproxyServer.objects.filter(GroupID=HaproxyGroup.objects.get(GroupID=groupid))
            canbindserver = HaproxyServer.objects.filter(GroupID__isnull=True)

            return HttpResponse(json.dumps({'BindedServer': dict([(i.ServerID, i.ServerIP) for i in bindedserver]),
                                            'CanBindServer': dict([(i.ServerID, i.ServerIP) for i in canbindserver])}))

        else:

            LoginName = request.session['LoginName']
            WaitForCreateAnsibleHostsFile = BoolInfo.objects.get(id=1).WaitForCreateAnsibleHostsFile
            allserver = HaproxyServer.objects.all()
            allgroup = HaproxyGroup.objects.all()
            # group_with_server = {}
            # for group in allgroup:
            #     ForeignKey_server = group.haproxyserver_set.all()
            #     group_with_server[group.GroupID] = ForeignKey_server


            return render(request, "haproxyedit.html", {'LoginName': LoginName,
                                                        'HaproxyServer': allserver,
                                                        'HaproxyGroup': allgroup,
                                                        'WaitForCreateAnsibleHostsFile': WaitForCreateAnsibleHostsFile})
    else:
        postdata = request.POST
        if 'HG_Select_GroupID' in postdata:
            result = {'state': 'success'}
            GroupMemberList = postdata.getlist('HG_Select_GroupMember')
            GroupID = postdata['HG_Select_GroupID']
            try:
                Group = HaproxyGroup.objects.get(GroupID=GroupID)
                OldMember = [i.ServerID for i in Group.haproxyserver_set.all()]
                DelMember = list(set(OldMember) - set(GroupMemberList))
                NewMember = list(set(GroupMemberList) - set(OldMember))

                # 删组成员
                map(lambda x: HaproxyServer.objects.filter(ServerID=x).update(GroupID=None), DelMember)
                # 加组成员
                map(lambda x: HaproxyServer.objects.filter(ServerID=x).update(GroupID=Group), NewMember)

                BoolInfo.objects.filter(id=1).update(WaitForCreateAnsibleHostsFile=True)

            except HaproxyServer.DoesNotExist or HaproxyGroup.DoesNotExist:
                result = {'state': 'false', 'msg': '无效ID！'}

        if 'createansiblefile' in postdata:

            import StringIO
            fs = StringIO.StringIO()
            allgroup = HaproxyGroup.objects.all()

            for eachgroup in allgroup:
                string_eachgroup = '''[{}]\n#{}\n{}\n\n'''.format(eachgroup.GroupName.encode('utf8'),
                                                                eachgroup.GroupComment.encode('utf8'),
                                                                '\n'.join(
                                                                    [i.ServerIP.encode('utf8') + ':' +
                                                                     str(THE_SSH_PORT)
                                                                     for i in eachgroup.haproxyserver_set.all()
                                                                     ]
                                                                ))
                fs.write(string_eachgroup)

            fs.seek(0)
            hostsfile = open(ANSILBE_HAPROXYHOSTS, 'w')
            hostsfile.write(fs.read())

            hostsfile.close()
            fs.close()
            BoolInfo.objects.filter(id=1).update(WaitForCreateAnsibleHostsFile=False)

            return HttpResponseRedirect('/haproxyedit/')

        goodpostdata = check_ip_and_separate_operation(postdata)
        if not goodpostdata:
            result = {'state': 'false', 'msg': '无效IP！'}

        else:
            if goodpostdata['table'] == 'HG':
                # HaproxyGroup操作
                target = goodpostdata['target']
                result = {'state': 'success'}

                if goodpostdata['operation'] == 'Add':
                    # 组添加操作
                    # print target['groupname']
                    if '' in target.values():
                        result = {'state': 'false', 'msg': '参数欠缺'}

                    elif not re.match(r'^[a-zA-Z]\w{1,19}$', target['groupname']):
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
                    # checkgroupname = re.compile(r'[a-zA-Z]\w{1,19}')
                    # 组编辑操作
                    if '' in target.values():
                        result = {'state': 'false', 'msg': '参数欠缺'}

                    elif not re.match(r'^[a-zA-Z]\w{1,19}$', target['groupname']):
                        result = {'state': 'false', 'msg': '组名只能使用大小写字母数字与下划线'}

                    else:
                        try:
                            updatedb = HaproxyGroup.objects.get(GroupID=target['id'])
                            updatedb.GroupName = target['groupname']
                            updatedb.GroupComment = target['comment']
                            updatedb.ServerConfigFilePath = target['configfilepath']
                            updatedb.GroupDisplayName = target['groupdisplayname']
                            updatedb.save()
                        except IntegrityError:
                            result = {'state': 'false', 'msg': '组名重复'}

                elif goodpostdata['operation'] == 'Del':
                    try:
                        HaproxyGroup.objects.get(GroupID=target['id']).delete()
                    except HaproxyGroup.DoesNotExist:
                        result = {'state': 'false', 'msg': '无效组ID'}

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


def aclrule(request):
    if 'LoginName' not in request.session:
        # 用户未登录跳转
        return HttpResponseRedirect('/login')
    if request.method == 'GET':
        return render(request, 'acl.html')


def webbackendcluster(request):
    if 'LoginName' not in request.session:
        # 用户未登录跳转
        return HttpResponseRedirect('/login')
    if request.method == 'GET':
        allbackend = WebBackendCluster.objects.all().order_by('-CreateTime')
        return render(request, 'webbackendcluster.html', {'AllBackend': allbackend})

    else:
        # print request.POST
        SERVERSLIST_RE = re.compile(r'^((\d{1,3}\.){3}\d{1,3}:\d{1,5},)*(\d{1,3}\.){3}\d{1,3}:\d{1,5}$')
        if 'WBC_Add_BackendClusterName' in request.POST:
            backendclustername = request.POST['WBC_Add_BackendClusterName']
            serverslist = ''.join(request.POST['serverslist'].split(' '))
            comment = request.POST['comment']
            if not re.match(r'^[a-zA-Z]\w{1,19}$', backendclustername):
                return HttpResponse(json.dumps({'falsemsg': '无效的集群名'}))
            elif not SERVERSLIST_RE.match(str(serverslist)):
                return HttpResponse(json.dumps({'falsemsg': '无效的后端服务器IP'}))
            try:
                wdb = WebBackendCluster(BackendID=UUID_TO_MD5_CharField('WBC'),
                                        BackendClusterName=backendclustername,
                                        BackendServersList=serverslist,
                                        Comment=comment)
                wdb.save()
                allbackend = WebBackendCluster.objects.all().order_by('-CreateTime')
                return render(request, 'webbackendcluster.html', {'AllBackend': allbackend})

            except Exception:
                return HttpResponse(json.dumps({'falsemsg': '数据库写入错误'}))

        elif 'WBC_Del_BackendClusterID' in request.POST:
            WBC_Del_BackendClusterID = request.POST['WBC_Del_BackendClusterID']
            try:
                ddb = WebBackendCluster.objects.get(BackendID=WBC_Del_BackendClusterID)
                ddb.delete()
                allbackend = WebBackendCluster.objects.all().order_by('-CreateTime')
                return render(request, 'webbackendcluster.html', {'AllBackend': allbackend})
            except WebBackendCluster.DoesNotExist:
                return HttpResponse(json.dumps({'falsemsg': '无效ID'}))

        elif 'WBC_Modify_BackendClusterID' in request.POST:
            WBC_Modify_BackendClusterID = request.POST['WBC_Modify_BackendClusterID']
            WBC_Modify_BackendClusterName = request.POST['WBC_Modify_BackendClusterName']
            WBC_Modify_BackendClusterServersList = ''.join(request.POST['WBC_Modify_BackendClusterServersList'].split(' '))
            WBC_Modify_BackendClusterComment = request.POST['WBC_Modify_BackendClusterComment']
            if not re.match(r'^[a-zA-Z]\w{1,19}$', str(WBC_Modify_BackendClusterName)):
                return HttpResponse(json.dumps({'falsemsg': '无效的集群名'}))
            elif not SERVERSLIST_RE.match(str(WBC_Modify_BackendClusterServersList)):
                return HttpResponse(json.dumps({'falsemsg': '无效的后端服务器IP'}))
            try:
                udb = WebBackendCluster.objects.get(BackendID=WBC_Modify_BackendClusterID)
                udb.BackendClusterName = WBC_Modify_BackendClusterName
                udb.BackendServersList = WBC_Modify_BackendClusterServersList
                udb.Comment = WBC_Modify_BackendClusterComment
                udb.save()
                allbackend = WebBackendCluster.objects.all().order_by('-CreateTime')
                return render(request, 'webbackendcluster.html', {'AllBackend': allbackend})
            except WebBackendCluster.DoesNotExist:
                return HttpResponse(json.dumps({'falsemsg': '无效ID'}))


