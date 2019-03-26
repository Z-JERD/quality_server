"""DEMO URL Configuration

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

from django.conf.urls import url,include
from rest_framework import routers
from AI_qast import views
router = routers.DefaultRouter()
router.register(r'quality_rule', views.QualityRuleModelView)
router.register(r'condition', views.ConditionModelView)





app_name = 'api'
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'analysis', views.AnalysisModelView.as_view()),

]