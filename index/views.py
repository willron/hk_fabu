# Create your views here.
# -*- coding:utf-8 -*-
from public.publicvar import *
from public.publicfunction import *
from django.shortcuts import render, HttpResponse, render_to_response
from index.models import UserLoginInfo, Logging
from projectinfo.models import Project
from django.http import HttpResponseRedirect
import commands
import os
import datetime
import json
import zipfile
import tarfile
import re


# ANSILBE_HOSTS = '/etc/ansible/hosts.bak'        # ansible的hosts文件路径
# # ANSILBE_HOSTS = '/home/fabu/.ansible/hosts.bak'        # ansible的hosts文件路径
# fabu_yml_path = '/home/fabu/ansible_playbook/fabu.yml '     # 用于升级发布时的playbook文件路径
# NEWFABU_YML_PATH = '/home/fabu/ansible_playbook/newfabu.yml '       # 用于全新发布时的playbook文件路径
# ansible-playbook命令
cmd = 'ansible-playbook %s --extra-vars "project_name=%s project_pack=%s project_port=%s backup_time=%s" -f %d -v'


# def read_project_name(section=None):
#     """
#     从hosts文件中获取项目名
#     :param section:项目名。如给定了项目名，则返回该项目的服务器列表
#     :return:列表
#     """
#     # all_project_name = Project.objects.values_list('project_name', 'project_server')
#
#     conf = ConfigParser.ConfigParser()
#     conf.read(ANSILBE_HOSTS)
#     if section:
#         return conf.options(section)
#     return conf.sections()


def runplaybook(yml_path, project_pack, project_name, project_port, backup_time, num):
    """
    运行ansible-playbook命令
    :param yml_path: playbook脚本(yml文件)路径
    :param project_pack: 压缩包路径
    :param project_name: 项目名
    :param backup_time: 备份文件文件名中的时间
    :param num: 线程数量==项目服务器数量
    :return: 运行状态, output输出
    """
    status, output = commands.getstatusoutput(cmd % (yml_path, project_name, project_pack, project_port, backup_time, num))
    return status, output


def check_ascii(filename_str):
    has_ascii_reg = re.compile(r'[^a-zA-Z0-9\./_-]')
    has_ascii = has_ascii_reg.findall(filename_str)
    if len(has_ascii) > 0:
        return False
    else:
        return True


def check_pack(pack_path, project_name):
    """
    检测压缩包是否规范，父目录需为 tomcat_项目名
    :param pack_path: 压缩包路径
    :param project_name: 项目模块名
    :return: 布尔
    """
    if pack_path.endswith('.zip'):      # zip包
        try:
            zf = zipfile.ZipFile(pack_path, mode='r')
            filename_lists = zf.filelist
            filename_str = ''.join([i.filename for i in filename_lists])
            has_ascii = check_ascii(filename_str)
            if not has_ascii:
                return '检测到文件名或路径含有非法字符！'
            for i in filename_lists:
                if not i.filename.startswith('tomcat_%s' % project_name):
                    return False
        except IOError:
            return '压缩包读取失败！'
        except UnicodeDecodeError:
            zf.close()
            return '检测到文件名或路径含有非法字符！'

    else:
        # 非zip包
        try:
            tf = tarfile.open(pack_path)
            filename_lists = tf.getnames()
            filename_str = ''.join(filename_lists)
            has_ascii = check_ascii(filename_str)
            if not has_ascii:
                return '检测到文件名或路径含有非法字符！'
            for i in filename_lists:
                if not i.startswith('tomcat_%s' % project_name):
                    return False
        except IOError:
            return '压缩包读取失败！'
        except UnicodeDecodeError:
            tf.close()
            return '检测到文件名或路径含有非法字符！'

    return True


def login(request):
    """
    用户登录处理函数
    :param request:
    :return:
    """
    if request.POST:
        LoginName = request.POST['LoginName']       # 获取登录名
        LoginPassword = request.POST['LoginPassword']       # 获取密码

        try:        # 数据库查询
            getUserInfo = UserLoginInfo.objects.get(user=LoginName, password=LoginPassword)
        except UserLoginInfo.DoesNotExist:      # 数据库无对应数据时产生异常则返回错误信息
            return render(request, 'login.html', {'LoginErrMsg': '用户名或密码错误'})

        if getUserInfo:
            # 将用户登录名以及用户的ftp路径写入session
            request.session['LoginName'] = LoginName
            request.session['ftp_path'] = getUserInfo.ftp_path
            return HttpResponseRedirect('/')
    else:
        request.session.set_expiry(3600*6)
        return render(request, 'login.html')


def index(request):
    """
    发布提交页面主处理函数
    :param request:
    :return:
    """

    if 'LoginName' not in request.session:
        # 用户未登录跳转
        return HttpResponseRedirect('/login')

    if request.POST:
        # 操作提交

        # 项目模块或压缩包未选择
        if request.POST['project_name'] == u'=====请选择=====' or request.POST['project_pack'] == u'=====请选择=====':
            return HttpResponse('<h1>项目模块或压缩包未选择！</h1>')

        project_pack = os.path.join(request.session['ftp_path'], request.POST['project_pack'])     # 拼接压缩包完整路径
        project_name = request.POST['project_name']     # 获取前端返回的项目模块名
        project_pack_md5check = request.POST['md5check'].lower()        # 获取前端返回的md5值，并转换为小写
        runplaybook_state = 'Done'      # runplaybook状态初始化为Done

        pack_md5 = commands.getoutput("/usr/bin/md5sum %s|awk '{print $1}'" % project_pack)     # 获取压缩包的md5值
        if project_pack_md5check != pack_md5:       # 前端返回的md5值与发布机上压缩包的md5值不匹配则返回错误信息
            return HttpResponse('<h1>MD5值不匹配，请重新上传压缩包！</h1>')

        # 检查压缩包打包规范
        check_pack_standard = check_pack(project_pack, project_name)

        if check_pack_standard != True:

            return HttpResponse('<h1>压缩包不规范！</h1>') if check_pack_standard == False \
                else HttpResponse('<h1>%s</h1>' % check_pack_standard)

        server_list = read_project_name(project_name)       # 获取模块服务器列表

        (the_yml_path, str_fabu) = (NEWFABU_YML_PATH, '(全新部署)') if 'newfabu' in request.POST else (FABU_YML_PATH, '(增量部署)')    # 判断是否为全新发布

        if 'newfabu' not in request.POST:
        #     for i in server_list:
        #         check_name_status, check_name_output = commands.getstatusoutput("/usr/bin/ssh -p 9055 tomcat@%s 'ls /opt/tomcat_%s'" % (i, project_name))
        #         if check_name_status == 0:
        #             return HttpResponse('<h1>服务器上检测到已有同名项目模块！</h1>')
        #
        # else:
            for i in server_list:
                check_name_status, check_name_output = commands.getstatusoutput("/usr/bin/ssh -p 9055 tomcat@%s 'ls /opt/tomcat_%s'" % (i, project_name))
                if check_name_status != 0:
                    return HttpResponse('<h1>服务器上无此项目模块，请确认是否为全新发布！</h1>')

        # 获取服务器当前时间
        backup_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        # 获取项目模块端口号
        project_port = Project.objects.get(project_name='[%s]' % project_name).project_port

        # 运行ansible-playbook
        status, output = runplaybook(the_yml_path, project_pack, project_name, project_port, backup_time, len(server_list))

        output_list = output.split('\n')        # 获取ansible-playbook输出
        RunPlaybookOutput = []      # 输出到前端页面的运行状态信息
        for i, value in enumerate(output_list):     # 检测失败信息
            if value.strip().startswith('fatal:'):
                RunPlaybookOutput.append(value)
                runplaybook_state = 'False'     # 出现失败信息则将runplaybook运行状态变更为False

        if len(RunPlaybookOutput) == 0:
            RunPlaybookOutput.append(runplaybook_state)

        try:        # 写入日志
            logging = Logging(state=runplaybook_state + str_fabu, user=request.session['LoginName'],
                              project_name=project_name, dest_server=server_list, log_date=output,
                              operation='Deployment', deployment_pack=request.POST['project_pack'])
            logging.save()
        except Logging:
            print 'write log false!'

        # 渲染返回
        return render(request, 'result.html', {'RunPlaybookState': RunPlaybookOutput})

    else:
        request.session.set_expiry(3600*6)
        ftp_path = request.session['ftp_path']      # 获取session中的用户ftp文件夹路径

        dir_list = os.listdir(ftp_path)     # 获取用户ftp文件夹下的文件列表
        file_list = []
        for i in dir_list:
            full_path = os.path.join(ftp_path, i)       # 获取完整文件路径
            if os.path.isfile(full_path) and (full_path.endswith('.tar.gz') or full_path.endswith('.zip') or
                                                  full_path.endswith('.tar') or full_path.endswith('.tgz')):
                # 排除其他文件，只取压缩包
                file_list.append(i)

        project_lists = read_project_name()     # 获取项目名

        Deployment_log = Logging.objects.filter(operation='Deployment').order_by('-ctime')[0:11]

        foradmin = 'block' if request.session['LoginName'] == 'admin' else 'none'
        # 渲染返回
        return render(request, 'index.html', {'project_pack': file_list,
                                              'project_lists': project_lists,
                                              'Deployment_log': Deployment_log,
                                              'foradmin': foradmin,
                                              'LoginName': request.session['LoginName']})

def GetProjectServerIP(request):
    if 'LoginName' not in request.session:
        # 用户未登录跳转
        return HttpResponseRedirect('/login')

    if 'LoginName' not in request.session:
        # 用户未登录跳转
        return HttpResponseRedirect('/login')

    elif request.GET['project_name']:
        projectname = request.GET['project_name']
        projectinfo = Project.objects.get(project_name='[%s]' % projectname)
        result = {'project_name': projectinfo.project_name.strip('[]'),
                  'project_server': projectinfo.project_server.replace(',', '</br>').replace(':9055', ''),
                  'project_port': projectinfo.project_port}
        return HttpResponse(json.dumps(result))


def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect('/login')


# def rollback(request):
#     if 'LoginName' not in request.session:
#         # 用户未登录跳转
#         return HttpResponseRedirect('/login')
#     if request.POST:
#         # 操作提交
#         pass
#     else:
#         return render(request, 'rollback.html', {'project_lists': read_project_name()})



