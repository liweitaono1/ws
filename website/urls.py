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
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from article import views
from article.api import FollowListView, ArticleCommit, MeArticleListView, ArticleListView, CategoryView, \
    ArticleCommintView, ArticleCommentReplyView, ArticleCreated
from course.views import CoursesList, MeCoursesList, CourseCreatedList, CourseListCreated
from forum.api import Forum_plateView, ForumView, CommentView, Parent_CommentView
from support.views import BannerList, EmailsList, LinkList, QQList, SeoList
from user.views import test, captcha_refresh, login_view, logout_view, to_login, Register, yan, getClbackQQ, \
    get_message, PersonApi, UserMessages, UserGetInfo, UserGetAllInfo, PersonOthers
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register('article_list', ArticleListView)
router.register('me_article_list', MeArticleListView)
router.register('ArticleCommit', ArticleCommit)
router.register('follow_list', FollowListView)
router.register('category', CategoryView)
router.register('article_Comment', ArticleCommintView)
router.register('comment_reply', ArticleCommentReplyView)
router.register('PersonApi', PersonApi)
router.register('info', UserGetInfo)
router.register('all_info', UserGetAllInfo)
# router.register('user_disbale', UserDisbale)
router.register('PersonOthers', PersonOthers)
router.register('UserMessages', UserMessages, base_name='UserMessages')
router.register('article', ArticleCreated)
router.register('courseList', CoursesList)
router.register('mecourseList', MeCoursesList)
router.register('course', CourseCreatedList)
router.register('Addtutorial', CourseListCreated)
router.register('BannerList', BannerList)
router.register('EmailsList', EmailsList)
router.register('LinkList', LinkList)
router.register('forum/category', Forum_plateView)
router.register('forum', ForumView)
router.register('CommentView', CommentView)
router.register('Parent_CommentView', Parent_CommentView)
router.register('get-list',QQList)
router.register('seo-list',SeoList,basename='seo-list')
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
    path('info/', get_message, name='info'),
    url(r'api/', include(router.urls)),
    re_path(r'api/login/$', obtain_jwt_token),  # jwt认证

]
