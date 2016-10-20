#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from projectinfo.models import Project
from index.models import Logging
from public.publicvar import *
import StringIO
import ConfigParser
import re


#the_ssh_port = 9055     # 服务器默认SSH端口，会统一加到ansible的hosts文件中
#ansible_hosts = '/home/fabu/.ansible/hosts'        # ansible的hosts文件路径

re_find_project_name = re.compile(r'^\[[0-9a-zA-Z_]{,30}\]:.*')       # 允许的项目名

# ipv4地址的正则匹配
re_ipv4 = re.compile(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
                     r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
                     r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
                     r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
re_remark = re.compile(r'^#.*$')        # 注释文本的正则匹配


class ProjectInfoInputError(Exception):
    """
    自定义异常类，于检测到前端输入错误时引发异常
    """
    def __init__(self, x):
        Exception.__init__(self, x)
        self.x = x


def _add_port(x, port):
    """
    为项目列表的ip添加端口
    :param x: 项目列表：[{’项目名1‘：{'ip':[ip列表],'msg':'注释文本信息'}},{’项目名2‘：{'ip':[ip列表],'msg':'注释文本信息'}}]
    :param port: 服务器默认SSH端口
    :return: 添加端口后的项目列表
    """
    add_del = x
    for i, v in enumerate(add_del):
        for a in range(len(add_del[i][v.keys()[0]]['ip'])):
            add_del[i][v.keys()[0]]['ip'][a] = add_del[i][v.keys()[0]]['ip'][a] + ':%s' % str(port)
    return add_del


def projectinfo(request):
    """
    /projectinfo/页面处理函数
    :param request:
    :return:
    """
    if 'LoginName' not in request.session:
        # 检查是否登录
        return HttpResponseRedirect('/login')
    if request.session['LoginName'] != 'admin':
        return HttpResponseRedirect('/')
    if request.POST:
        # 页面POST返回数据处理
        try:
            # 检测POST过来的项目信息格式，检测过程遇到非法格式则触发自定义异常

            # 去除整段项目信息文本的段前段后空白，并按行拆分为列表
            projectinfo_input_list = request.POST['projectinfo'].strip().split('\n')
            # 去除列表各项文本的行前行后空白
            projectinfo_input_list = map(lambda x: x.strip(), [i for i in projectinfo_input_list])
            project_lists = []

            if not re_find_project_name.match(projectinfo_input_list[0]):
                # 首先非[项目名]开始则异常
                raise ProjectInfoInputError('输入格式有误！')

            for i, v in enumerate(projectinfo_input_list):
                # 项目信息检测主逻辑

                # project_dict = {}       # 单个项目

                if re.match(r'^$', v):
                    # 跳过空行
                    continue

                if v.endswith(']') or v.endswith(':'):
                    raise ProjectInfoInputError('似乎有端口忘了输入！')

                if re_find_project_name.match(v):
                    # 检测到[项目名]则进入for
                    project_ip = []
                    project_msg = ''
                    # 项目名格式查错，分离项目名与项目端口
                    project_name_port = v.split(':')
                    if len(project_name_port) != 2:
                        raise ProjectInfoInputError('输入格式有误！')

                    if project_name_port[1].isnumeric():
                        if 80 <= int(project_name_port[1]) <= 65535:
                            project_port = project_name_port[1]
                        else:
                            raise ProjectInfoInputError('端口范围必须为80-65535！')
                    else:
                        raise ProjectInfoInputError('输入格式有误！')

                    v = project_name_port[0]

                    # if not 10 <= int(project_port) <= 65535:
                    #     # 检查项目端口是否正确
                    #     raise ProjectInfoInputError('端口输入有误！')

                    for k in projectinfo_input_list[i + 1:]:
                        # 检索[项目名]后面的内容

                        if re.match(r'^$', k):
                            # 跳过空行
                            continue

                        if re_find_project_name.match(k):
                            # 如果再次检测到[项目名]则跳出项目内容检索
                            break

                        if re_remark.match(k):
                            # 检索到注释
                            project_msg = project_msg + re_remark.match(k).group(0)

                        if re_ipv4.match(k):
                            # 检索到ipv4地址
                            project_ip.append(k)

                    project_dict = dict([(v, dict([
                        ('msg', project_msg),
                        ('ip', project_ip),
                        ('project_port', project_port)
                    ]))])

                    if len(project_dict[v]['ip']) >= 1:
                        # ipv4地址列表存在则视为有效信息并添加到project_lists列表
                        project_lists.append(project_dict)

            # 检查项目端口是否有重复
            all_project_port = [each.values()[0]['project_port'] for each in project_lists]
            if len(set(all_project_port)) != len(all_project_port):
                raise ProjectInfoInputError('有重复的端口！')

            add_port = _add_port(project_lists, port=the_ssh_port)       # 为IP地址添加端口

            write_line = []
            # 将项目信息转换为列表以便写入hosts文件
            for i in add_port:
                write_line.append(i.keys()[0] if not write_line else '\n' + i.keys()[0])
                write_line.append(i.values()[0]['msg'])
                write_line.append('\n'.join(i.values()[0]['ip']))

            # 利用StringIO模块将项目信息存为内存文件以便使用ConfigParser进行最后检测
            f = StringIO.StringIO()
            f.write('\n'.join(write_line))
            f.seek(0)

            try:        # 使用ConfigParser进行最后检测
                conf = ConfigParser.ConfigParser()
                conf.readfp(f)
            except ConfigParser.Error:      # ConfigParser模块异常则触发自定义异常
                raise ProjectInfoInputError('难以发现的格式错误！')

            try:        # 写入hosts文件
                f.seek(0)       # 指针回位
                with open(ansible_hosts, 'w') as hosts:
                    hosts.write(f.read().encode("UTF-8"))
            except IOError:
                raise ProjectInfoInputError('ansible hosts文件写入失败')

            for i in project_lists:
                try:        # 数据库写入
                    w_db = dict([
                        ('project_name', i.keys()[0]),
                        ('project_msg', i.values()[0]['msg']),
                        ('project_server', ','.join(i.values()[0]['ip'])),
                        ('project_port', int(i.values()[0]['project_port']))
                    ])

                    # 项目信息更新或新建
                    Project.objects.update_or_create(project_name=w_db['project_name'], defaults=w_db)

                    # 日志写入
                    w_logging = Logging(state='Done', user=request.session['LoginName'],
                                        project_name=w_db['project_name'], dest_server=w_db['project_server'],
                                        log_date=w_db['project_msg'], operation='ModefyProject')
                    w_logging.save()

                except:
                    raise ProjectInfoInputError('数据库写入失败！')

            try:        # 删除多余的项目
                # 获取数据库中所有项目名称
                all_project_indb = Project.objects.values_list('project_name')

                # 获取多余的项目名
                del_project = list(set(x[0] for x in all_project_indb) - set([x.keys()[0] for x in project_lists]))

                # 删除多余项目
                map(lambda x: Project.objects.get(project_name=x).delete(), del_project)

                # 删除项目-日志写入
                map(lambda x: Logging.objects.create(user=request.session['LoginName'],
                                                     project_name=x, state='Done',
                                                     dest_server='DELETE',
                                                     log_date='DELETE',
                                                     operation='ModefyProject'), del_project)

            except:
                raise ProjectInfoInputError('数据库写入失败！')

            f.close()       # 内存文件关闭

        except ProjectInfoInputError, e:
            return render(request, 'projectinfo.html', {'ProjectInfoInputError': e,
                                                        'projectinfo': projectinfo_input_list})

        return HttpResponse('<h1>操作成功</h1><br /><a href="">返回</a>')
    else:
        # GET页面请求
        all_project = Project.objects.all()     # 获取数据库所有项目
        projectinfo_input_list = []
        for each_project_obj in all_project:
            # 以 项目名 项目注释 项目IP列表 为次序，顺序添加进projectinfo_input_list列表

            # 如果不是第一个项目则在项目名前添加换行，利于前端页面的展示
            send_project_name = each_project_obj.project_name + ':' + str(each_project_obj.project_port)
            projectinfo_input_list.append(send_project_name if not projectinfo_input_list else '\n' + send_project_name)
            # 添加注释
            projectinfo_input_list.append(each_project_obj.project_msg.replace('#', '\n#').strip())
            # 遍历项目IP并按顺序添加
            for i in each_project_obj.project_server.split(','):
                projectinfo_input_list.append(i.split(':')[0])
        # 渲染返回
        return render(request, 'projectinfo.html', {'projectinfo': projectinfo_input_list,
                                                    'LoginName': request.session['LoginName']})
