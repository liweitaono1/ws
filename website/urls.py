"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from article import views
from user.views import test, captcha_refresh, login_view, logout_view, to_login, Register, yan, getClbackQQ
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', test),  # 这是生成验证码的图片
    url(r'^captcha/', include('captcha.urls')),
    path('refresh/', captcha_refresh),  # 这是生成验证码的图片
    path('login/', login_view, name='index'),
    path('logou/', logout_view, name='logou'),
    path('register/', Register.as_view(), name='register'),
    path('yan/', yan),
    path('', views.Article_list, name='home'),
    url('auth-qq', to_login, name='qq-login'),
    path('person/', include('apps.user.urls', namespace='user')),
    path('article/', include('apps.article.urls', namespace='article')),
    path('course/', include('apps.course.urls', namespace='course')),
    path('forum/', include('apps.forum.urls', namespace='forum')),
    path('support/', include('apps.support.urls', namespace='support')),
    url(r'^search/', include('haystack.urls'), name='haystack_search'),
    url('getClbackQQ', getClbackQQ, name='getClbackQQ'),

]
