"""hk_fabu2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
# from django.contrib import admin
from index import views as index_views
from projectinfo import views as projectinfo_views
from rollback import views as rollback_views
from startstoprestart import views as startstoprestart_views
from haproxyedit import views as haproxyedit_views
from haproxyedit import groupruleedit as groupruleedit_views
from showlogs import views as showlogs_views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', index_views.index, name='index'),
    url(r'^login/$', index_views.login, name='login'),
    url(r'^projectinfo/$', projectinfo_views.projectinfo, name='projectinfo'),
    url(r'^GetProjectServerIP/$', index_views.GetProjectServerIP, name='GetProjectServerIP'),
    url(r'^logout/$', index_views.logout, name='logout'),
    url(r'^rollback/$', rollback_views.rollback, name='rollback'),
    url(r'^GetBackupName/$', rollback_views.get_backup_name, name='get_backup_name'),
    url(r'^startstoprestart/$', startstoprestart_views.startstoprestart, name='startstoprestart'),
    url(r'^haproxyedit/$', haproxyedit_views.haproxyedit, name='haproxyedit'),
    url(r'^showlogs/$', showlogs_views.showlogs, name='showlogs'),
    url(r'^haproxyedit/(HG_[a-f0-9]{32})/$', groupruleedit_views.index, name='groupruleedit'),
    url(r'^haproxyedit/WebBackendCluster/$', haproxyedit_views.webbackendcluster, name='webbackendcluster'),
    url(r'^haproxyedit/ACLRule/$', haproxyedit_views.aclrule, name='aclrule'),
]

