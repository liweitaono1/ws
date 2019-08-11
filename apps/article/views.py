import datetime
import json
import os
import random

import requests
import urllib3
from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.pagination import PageNumberPagination

from article.forms import Article_form
from article.models import Article, Recommend, Category_Article, Headlines
from article.tasks import error_email
from forum.models import Forum
from support.models import *
from user.models import Follows
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from utils.jsonserializable import DateEncoder

User = get_user_model()


def test(request):
    WorkList = []
    for i in range(1, 100):
        WorkList.append(Forum(
            title='```cpp\n下例 中的某些语句读不太明白：\n 1.   DataTable dt=ds.Tables[\"cs\"] 这句最难理解，意思是读取cs表赋给新建的内存表dt（复制表）?还是dt表指向（引用）cs表，修改dt其实就是修改cs?\n 2.   sda.FillSchema(dt,SchemaType.Mapped); 这句应该是将数据库表中的元数据填入到dt中，为何要填入?cs表中没有元数据吗?\n 3.   此例中修改了dt表，执行Update为何更新了数据库?dt、cs与数据库是个怎么个联系?\n\n\n例：\nSqlConnection ds;\nDataSet ds;\nSqlDataAdapter sda;\n...........        \nDataTable dt=ds.Tables[\"cs\"];\nsda.FillSchema(dt,SchemaType.Mapped);\nDataRow dr=dt.Rows.Find(txtNo.text);\ndr[\"姓名\"]=txtName.Text.Trim();\ndr[\"性别\"]=txtSex.Text.Trim();\nSqlCommandBuilder cmdbuilder=new SqlCommandBuilder(sda);\nsda.Update(dt);\n```%s' % (
                i), category_id=4, authors_id='7d4d01419d1d491ab7c399b3c965b'))
    Forum.objects.bulk_create(WorkList)
    return HttpResponse('ok')


def Article_list(request):
    '''
    首页
    :param request:
    :return:
    '''
    from support.models import link
    article = Article.objects.filter(is_show=True)[:100]
    popular = Article.objects.filter(is_show=True).order_by('click_nums')[:5]
    recommend = Recommend.objects.filter(is_recommend=True)[:10]
    qq = QQ.objects.all()
    links = link.objects.all()

    user = Follows.objects.values('follow_id').distinct().order_by('-follow_id')
    item = []
    for i in user:
        data = {}
        data['data'] = User.objects.filter(follow__follow__id=i['follow_id']).distinct()
        item.append(data)

    try:
        page = request.GET.get('page', 1)
        if page == '':
            page = 1

    except PageNotAnInteger:
        page = request.GET.get('page')
    p = Paginator(article, 10, request=request)
    people = p.page(page)
    if request.is_ajax():
        json_dict = {}
        json_dict['data'] = []
        data = p.page(page).object_list
        print(people.has_next())
        json_dict['status'] = people.has_next()
        json_dict['num_pages'] = people.num_pages
        json_dict['page'] = page
        for i in data:
            list_dict = {}
            list_dict = {}
            list_dict['title'] = i.title
            list_dict['id'] = i.id
            list_dict['username'] = i.authors.username
            list_dict['userId'] = i.authors.id
            list_dict['userImag'] = i.authors.user_imag
            list_dict['userImage'] = i.authors.user_image
            list_dict['category'] = i.category.name
            list_dict['click_nums'] = i.click_nums
            list_dict['desc'] = i.desc
            list_dict['list_pic'] = i.list_pic
            list_dict['add_time'] = i.add_time
            article_comment = i.article_comment_set.all()
            article_comment_childer = i.article_comment_set.count()
            for i in article_comment:
                article_comment_childer += i.articlecommentreply_set.count()
            json_dict['data'].append(list_dict)
        return JsonResponse(json_dict, safe=False, encoder=DateEncoder)
    banners = Banners.objects.first()
    return render(request, 'pc/index.html',
                  {'article': people, 'qq': qq, 'popular': popular, 'count': item, 'recommend': recommend,
                   'links': links, 'banners': banners})


def ArticleList(request):
    '''
    文章列表
    :param request:
    :return:
    '''
    article = Article.objects.filter(is_show=True)
    category = Category_Article.objects.all()
    type = request.GET.get('type', '')
    try:
        page = request.GET.get('page', 1)
        if type:
            article = article.filter(category_id=type)
            if page == '':
                page = 1
    except PageNotAnInteger:
        page = 1

    p = Paginator(article, 10, request=request)
    people = p.page(page)
    headlines = Headlines.objects.all()[:30]
    banners = Banners.objects.first()

    return render(request, 'pc/article.html',
                  {'article': people, 'category': category, 'Headlines': headlines, 'banners': banners})


def api(request):
    # TODO: 修改
    url = 'http://v.juhe.cn/toutiao/index?type=keji&key={0}'.format(conf.get('AppKey', 'key'))
    headers = {
        "Accept-Encoding": "gzip",
        "Connection": "close"
    }
    r = requests.get(url, headers=headers)
    print(r.json())
    if r.status_code == requests.codes.ok:
        dict_json = r.json()
        print(dict_json['result']['data'])
        main = Headlines()
        list_dict = []
        for item in dict_json['result']['data']:
            obj = Headlines(
                url=item['url'],
                title=item['title'],
                category=item['category'],
                conent=item['content'],
                author_name=item['author_name']
            )
            list_dict.append(obj)
        Headlines.objects.bulk_create(list_dict)
    cur_date = datetime.datetime.now().date()
    # 前四天
    day = cur_date - datetime.timedelta(days=7)
    # 查询前一周数据，也可以用range
    Headlines.objects.filter(add_time__lte=day).delete()
    return HttpResponse({'ee': '43'})


from apps.article.tasks import add, error_email, conf


def addModel(request):
    add.delay()
    print('定时任务')
    return HttpResponse('ok')


@login_required(login_url='/login')
def ArticleMe(request):
    '''
    我关注的人的文章
    :param request:
    :return:
    '''
    article = Article.objects.filter(authors__follow__fan_id=request.user.id, is_show=True)
    category = Category_Article.objects.all()
    type = request.GET.get('type', '')
    try:
        page = request.GET.get('page', 1)
        if type:
            article = Article.objects.filter(authors__follow__fan_id=request.user.id, category_id=type, is_show=True)
        if page == '':
            page = 1
    except PageNotAnInteger:
        page = 1
    p = Paginator(article, 10, request=request)
    people = p.page(page)
    headlines = Headlines.objects.all()[:20]
    banners = Banners.objects.first()
    return render(request, 'pc/article_me.html',
                  {'article': people, 'category': category, 'Headlines': headlines, 'banners': banners})


@login_required(login_url='/login')
def Article_Add(request):
    '''
    新增文章
    :param request:
    :return:
    '''
    if request.method == 'GET':
        category = Category_Article.objects.all()
        return render(request, 'pc/articlesadd.html', {"category": category})

    if request.method == 'POST':
        forms = Article_form(request.POST)
        if forms.is_valid():
            title = forms.cleaned_data.get('title')
            content = forms.cleaned_data.get('content')
            category = request.POST.get('category', '')
            desc = request.POST.get('desc', '')
            keywords = request.POST.get('keywords', '')
            list_pic = request.FILES.get('list_pic', '')
            authors = forms.cleaned_data.get('authors', '')
            article = Article()
            article.title = title
            article.content = content
            article.desc = desc
            article.keywords = keywords
            article.authors = authors
            article.category_id = int(category)
            article.list_pic = list_pic
            try:
                article.save()
                return JsonResponse({"code": 200, "data": "发布成功"})
            except Exception:
                return JsonResponse({"code": 400, "data": "发布失败"})
        return JsonResponse({"code": 400, "data": "验证失败"})


@login_required(login_url='/login')
def ArticleUpdate(request, article_id):
    """
    文章修改
    :param request:
    :param article_id:
    :return:
    """
    if request.method == 'GET':
        category = Category_Article.objects.all()
        try:
            article = Article.objects.get(id=article_id)
        except Exception:
            return Http404
        return render(request, 'pc/article_update.html', {'article': article, 'category': category})
    if request.method == 'POST':
        forms = Article_form(request.POST)
        if forms.is_valid():
            title = forms.cleaned_data.get('title')
            content = forms.cleaned_data.get('content')
            category = request.POST.get('category', '')
            desc = request.POST.get('desc', '')
            keywords = request.POST.get('keywords', '')
            type = request.POST.get('type', '')
            if type:
                list_pic = request.FILES.get('list_pic', '')
            else:
                list_pic = request.POST.get('list_pic', '')
            authors = forms.cleaned_data.get('authors', '')
            article = Article.objects.get(id=article_id)
            article.title = title
            article.content = content
            article.desc = desc
            article.keywords = keywords
            article.authors = authors
            article.category_id = int(category)
            article.list_pic = list_pic
            try:
                article.save()
                return JsonResponse({"code": 200, "data": "发布成功"})
            except Exception:
                return JsonResponse({"code": 400, "data": "发布失败"})
        return JsonResponse({"code": 400, "data": "验证失败"})


@require_POST
@csrf_exempt
def ArticleDelete(request):
    """
    删除文章
    :param request:
    :return:
    """
    if request.method == 'POST':
        id = json.loads(request.body)['id']
        user = json.loads(request.body)['username']
        if id and user:
            Article.objects.filter(id=id, authors_id=user).update(is_show=False)
            return JsonResponse({'status': 200, 'message': '删除成功'})
        return JsonResponse({'status': 400, 'message': '删除失败'})


@login_required(login_url='/login')
@require_POST
def RemoveImage(request, article_id):
    '''
    删除图片
    :param request:
    :param article_id:
    :return:
    '''
    if request.method == 'POST':
        article = Article.objects.get(id=article_id)
        article.list_pic = ''
        article.save()
        return JsonResponse({'data': 200})


def Article_detail(request, article_id):
    '''
    文章详情页
    :param request:
    :param article_id:
    :return:
    '''
    try:
        article = Article.objects.get(id=article_id)
        id = article.category.id
        article.click_nums += 1
        article.save()
    except Exception:
        return Http404

    content = Article.objects.filter(category_id=id).exclude(id=article_id).order_by('-click_nums')[:10]
    print(content.annotate())
    return render(request, 'pc/article_detail.html', {'article': article, 'id': article_id, 'content': content})


@csrf_exempt
@login_required(login_url='/login')
def blog_img_upload(request):
    '''
    写博客上传图片
    :param request:
    :return:
    '''
    if request.method == 'POST':
        data = request.FILES['editormd-image-file']
        img = Image.open(data)
        width = img.width
        height = img.height
        rate = 1.0  # 压缩率
        # 根据图像大小设置压缩率
        if width >= 2000 or height >= 2000:
            rate = 0.3
        elif width >= 1000 or height >= 1000:
            rate = 0.5
        elif width >= 500 or height >= 500:
            rate = 0.9
        width = int(width * rate)  # 新的宽
        height = int(height * rate)  # 新的高
        img.thumbnail((width, height), Image.ANTIALIAS)  # 生成缩略图
        url = 'blogimg/' + data.name
        print(request.build_absolute_uri(settings.MEDIA_URL + data.name))
        name = settings.MEDIA_ROOT + '/' + url
        while os.path.exists(name):
            file, ext = os.path.splitext(data.name)
            file = file + str(random.randint(1, 1000))
            data.name = file + ext
            url = 'blogimg/' + data.name
            name = settings.MEDIA_ROOT + '/' + url
        try:
            img.save(name)
            print(name)
            url = request.build_absolute_uri(settings.MEDIA_URL + 'blogimg/' + data.name)
            return JsonResponse({'success': 1, 'message': '成功', 'url': url})
        except Exception as e:
            return JsonResponse({'success': 0, 'message': '上传失败'})


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    # page_size_query_param = 'page_size'  # 每页设置展示多少条
    page_query_param = 'page'
    max_page_size = 100
