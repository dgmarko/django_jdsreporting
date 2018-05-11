from django.conf.urls import re_path, url
from django.urls import path
from . import views
from .views import Report_Output, Report
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.index, name='index'),
    path('data_input/', views.data_input, name='data_input'),
    url(r'report/$', login_required(Report.as_view(success_url="report/output")), name='report_view'),
    url(r'output/$', Report_Output.as_view(), name='report_output'),
]
