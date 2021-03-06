"""sas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, re_path
from django.contrib import admin

from . import views, testdb
import sys

sys.path.append("../")
from Login.views import login, register
from main.views import main, profile, comments, opinion, analysis

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'login/', login),
    path('register/', register),
    path(r'main/', main),
    path(r'profile/', profile),
    path(r'comments/', comments),
    re_path(r'^opinion/(?P<id>[0|1|2])/$', opinion),
    re_path(r'^analysis/(?P<product_id>[0|1|2])/(?P<phase>[0|1])/(?P<aspect>.+)', analysis),
    
]
