"""AI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from  django.conf.urls import url,include
from  AI_qast import rulecheck
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('AI_qast.urls', namespace='v1')),
    url(r'^check/', include('AI_check.urls', )),
    #url(r'^test/', include('checking.urls')),


    url(r'^rule_list/',rulecheck.rule_list),
    url(r'^rule_add/', rulecheck.rule_add),
    url(r'^rule_del/', rulecheck.rule_del),
    url(r'^condition_list/', rulecheck.condition_list),
    url(r'^condition_add/', rulecheck.condition_add),
    url(r'^condition_del/', rulecheck.condition_del),
    url(r'^check_list/', rulecheck.task_list),
    url(r'^add_check/', rulecheck.add_task),
    url(r'^delete_check/', rulecheck.delete_task),

    url(r'^get_result/', rulecheck.checkrequest),
    url(r'^conversation_rule/', rulecheck.sationrule),
]
