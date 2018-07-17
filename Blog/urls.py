"""Blog URL Configuration

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
from django.urls import path,re_path
from blog_CN import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('index/', views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('digg/', views.like),
    path('comment/', views.comment),
    path('background/', views.background),
    path("background/add_article/",views.add_article),
    path("upload/", views.upload),
    path("register/", views.register),
    path("code/",views.code),
    re_path("background/compile_article/(?P<article_id>\d+)/", views.compile_article),
    re_path('background/del_article/(?P<article_id>\d+)/',views.del_article),
    re_path('(?P<username>\w+)/(?P<condition>category|tag|achrive)/(?P<parms>.*)/',views.homePage),
    re_path('(?P<username>\w+)/articles/(?P<article_id>\d+)/', views.article_detail),
    re_path('(?P<username>\w+)/$', views.homePage),
]
