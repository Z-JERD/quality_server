




from django.conf.urls import url,include
from rest_framework import routers
from AI_check import views
router = routers.DefaultRouter()
router.register(r'task', views.QualityTaskModelView)


app_name = 'AI_check'

urlpatterns = [

    url(r'^', include(router.urls)),
    url(r'^task_check/', views.QualityCheckModelView.as_view()),
    url(r'^task_result/', views.CheckRequestModelView.as_view()),
    url(r'^task_rule/', views.ResultDetailModelView.as_view()),


]