from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import PageNotAnInteger
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from pure_pagination import Paginator

from forum.forms import Forum_form, ParentComment
from forum.models import Forum_plate, Forum, Parent_Comment
from user.models import UserMessage

User = get_user_model()
def get_online_count():
    online_ips = cache.get('online_ips',[])
    print(online_ips)
    if online_ips:
        online_ips = cache.get_many(online_ips).keys()
        return len(online_ips)
    return 0

def index(request):
    '''
    帖子首页
    :param request:
    :return:
    '''
    plate = Forum_plate.objects.all()
    forum = Forum.objects.filter(hidden=False)
    job = Forum.objects.filter(category__name='求职招聘')
    try:
        page = request.GET.get('page', 1)
        if page == '':
            page = 1
    except PageNotAnInteger:
        page = 1
        # Provide Paginator with the request object for complete querystring generation
    p = Paginator(forum, 10, request=request)
    people = p.page(page)
    return render(request, 'pc/forum.html', locals())

def indexMe(request):
    '''
    我的贴子首页
    :param request:
    :return:
    '''
    plate = Forum_plate.objects.all()
    forum = Forum.objects.filter(hidden=False)
    count= User.objects.filter(follow__fan__id=request.user.id)
    floow = User.objects.filter(fan__follow_id=request.user.id)
    try:
        page = request.GET.get('page', 1)
        if page == '':
            page = 1
    except PageNotAnInteger:
        page = 1
        # Provide Paginator with the request object for complete querystring generation
    p = Paginator(forum, 10, request=request)
    people = p.page(page)
    return render(request, 'pc/forum_me.html', locals())

@login_required(login_url='/login')
def add_forum(request):
    '''
    新增帖子
    :param request:
    :return:
    '''
    category = Forum_plate.objects.all()
    if request.method == 'POST':
        form = Forum_form(request.POST)
        if form.is_valid():
            forum  = Forum()
            forum.title = form.cleaned_data.get('title')
            forum.category_id = form.cleaned_data.get('category')
            forum.keywords = form.cleaned_data.get('keywords')
            forum.content = form.cleaned_data.get('content')
            forum.authors = form.cleaned_data.get('authors')
            try:
                forum.save()
                return JsonResponse({"code": 200, "data": "发布成功"})
            except Exception:
                return JsonResponse({"code": 400, "data": "发布失败"})
        return JsonResponse({"code": 400, "data": "发布失败"})
    return render(request, 'pc/forum_add.html', locals())


def forum_detail(request,forum_id):
    '''
    详情
    :param request:
    :return:
    '''
    dicts = get_object_or_404(Forum,pk=forum_id)
    dicts.click_nums += 1
    dicts.save()
    if request.method == 'POST':
        forms = ParentComment(request.POST)
        if forms.is_valid():
            try:
                data = Parent_Comment()
                data.forums = forms.cleaned_data.get('forums')
                data.user = forms.cleaned_data.get('user')
                data.comments = forms.cleaned_data.get('comments')
                data.parent_comments = forms.cleaned_data.get('parent_comments')
                data.to_Parent_Comments = forms.cleaned_data.get('to_Parent_Comments')
                data.url = forms.cleaned_data.get('url')
                data.address = request.POST.get('address')
                data.save()
                return JsonResponse({"code": 200, "data": "发布成功"})
            except Exception as e:
                return JsonResponse({"code": 400, "data": "发布失败"})
        return render(request, 'pc/forum_detail.html', {'dicts': dicts})



def forum_category(request,category):
    '''
    分类
    :param request:
    :return:
    '''
    cate_list = Forum.objects.filter(category_id=category,hidden=False)
    plate = Forum_plate.objects.all()
    job = Forum.objects.filter(category__name='求职招聘')
    type = get_object_or_404(Forum_plate,pk=category)
    try:
        page = request.GET.get('page', 1)
        if page == '':
            page = 1
    except PageNotAnInteger:
        page = 1
        # Provide Paginator with the request object for complete querystring generation
    p = Paginator(cate_list, 20, request=request)
    people = p.page(page)

    return render(request, 'pc/forum_category.html', locals())


def delForum(request):
    '''
    删除帖子
    :param request:
    :return:
    '''
    if request.is_ajax():
        try:
            data = get_object_or_404(Forum,pk=id)
            data.hidden=True
            data.save()
            return JsonResponse({'status':200,'message':'删除成功'})
        except Exception as e:
            return JsonResponse({'status': 400, 'message': '删除失败'})


@receiver(post_save,sender=Parent_Comment)
def my_callback_reply(sender,**kwargs):
    '''
    评论通知
    :param sender:
    :param kwargs:
    :return:
    '''
    try:
        message = UserMessage()
        message.user_id = kwargs['instance'].to_Parent_Comments_id
        message.ids = kwargs['instance'].forums_id
        message.to_user_id = kwargs['instance'].user.id
        message.has_read = False
        message.url =kwargs['instance'].url
        message.message = "你参与的 %s 帖子评论有人回复了,快去看看吧!"%kwargs['instance'].parent_comments.forums.title
        message.save()
    except Exception as e:
        pass
