import json
import random
import re
import time
from configparser import ConfigParser
from urllib import parse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from article.models import Category_Article, Article
from article.serializers import ArticleSerializer
from article.tasks import send_register_email
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.views import View
from pytz import unicode

from article.views import StandardResultsSetPagination
from user.filter import CategoryFilter
from user.forms import CaptchaTestForm, LoginForms, RegisterForm, EmailForm, ModifyForm, Follow_Forms, InfoForm
from user.models import UserMessage, VerifyCode, Follows, OAuthQQ
from user.serializers import UserSerializer, UserMessageSerializer
from utils.EmailToken import token_confirm
from utils.permissions import IsOwnerOrReadOnly

User = get_user_model()


def test(request):
    form = CaptchaTestForm()
    return render(request, 'test.html', {'form': form})


def captcha_refresh(request):
    '''return json with new captcha for ajax refresh request'''
    if not request.is_ajax():
        # 只接受ajax提交
        raise Http404
    new_key = CaptchaStore.generate_key()
    to_json_response = {
        'key': new_key,
        'image_url': captcha_image_url(new_key)
    }

    return JsonResponse(to_json_response)


def yan(request):
    cs = CaptchaStore.objects.filter(response=request.POST['response'], hashkey=request.POST['hashkey'])
    if cs:
        return JsonResponse({"valid": True})
    else:
        return JsonResponse({'valid': False})


class CustomBackend(ModelBackend):
    '''进行手机登录验证'''

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(email=username) | Q(username=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


def login_view(request):
    if request.method == 'GET':
        next = request.GET.get('next')
        if next:
            return render(request, 'pc/logoin.html', {'next': next})
        else:
            return render(request, 'pc/logoin.html')
    elif request.method == 'POST':
        form = LoginForms(request.POST)
        next = request.GET.get('next')
        if form.is_valid():
            telephone = form.cleaned_data.get('telephone')
            password = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            user = authenticate(request, username=telephone, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    if remember:
                        request.session.set_expiry(None)
                    else:
                        request.session.set_expiry(0)
                    if next:
                        return HttpResponseRedirect(next)
                    else:
                        return redirect(reverse('home'))
                else:
                    return render(request, 'pc/logoin.html', {'next': next, 'error': '此账号暂未激活，请联系管理员'})
                    # return JsonResponse({"code": 401, "message": "此账号暂未激活，请联系管理员", "data": {}})
                    # return restful.unauth(message='此账号暂无权限，请联系管理员')
            else:
                return render(request, 'pc/logoin.html', {'next': next, 'error': '账号或密码错误'})
                # return JsonResponse({"code": 400, "message": "账号或者密码错误", "data": {}})
                # return restful.params_error(message="手机号码或者密码错误")
        else:
            errors = form.get_errors()
            return render(request, 'pc/logoin.html', {'next': next, 'error': errors})
            # return JsonResponse({"code":400,"message":"","data":errors})
            # return restful.params_error(message=errors)


def logout_view(request):
    logout(request)
    return redirect('home')


class Register(View):
    '''
    注册
    '''

    def get(self, request):
        return render(request, 'pc/register.html')

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username', '')
            email = form.cleaned_data.get('email', '')
            password = form.cleaned_data.get('password', '')
            users = User()
            users.username = username
            users.password = make_password(password)
            users.email = email
            users.is_active = False
            users.save()
            token = token_confirm.generate_validate_token(username)
            message = '\n'.join([
                u'{0},欢迎加入我的博客'.format(username),
                u'请访问该链接,完成用户验证,该链接一个小时有效',
                '/'.join([
                    settings.DOMAIN,
                    'activate',
                    token])])
            # send_mail(u'注册用户验证信息', message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            send_register_email
            send_register_email(email=email, username=username, token=token, send_type='register')
            return JsonResponse({'valid': True, 'status': 200, 'message': u"请登录到注册邮箱中验证用户，有效期为1个小时"})
        return JsonResponse({'status': 400, 'data': form.errors, 'valid': False})


def active_user(request, token):
    '''
    激活验证
    :param request:
    :param token:
    :return:
    '''
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        username = token_confirm.remove_validate_token(token)
        users = User.objects.filter(username=username)
        for user in users:
            if user.is_active == False:
                user.delete()
                return render(request, 'pc/message.html', {
                    'message': u'对不起,验证链接已经过期,请重新<a href=\"' + unicode(settings.DOMAIN) + u'/register\">注册</a>'
                })
            else:
                return render(request, 'pc/message.html',
                              {'message': u'此账号已经验证过，请重新<a href=\"' + unicode(settings.DOMAIN) + u'/register\">注册</a>'})
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'pc/message.html', {
            'message': u'对不起，您所验证的用户不存在，请重新<a href=\"/register\">注册</a>'
        })
    user.is_active = True
    user.save()
    msg = UserMessage()
    msg.user = user
    msg.to_user = User.objects.get(is_superuser=True)
    msg.message = '欢迎加入本站,在使用过程中有什么疑问,请联系管理员'
    msg.has_read = False
    msg.is_supper = True
    msg.save()
    message = u'验证成功，请进行<a href=\"' + unicode(settings.DOMAIN) + u'/login\">登录</a>操作'
    return render(request, 'pc/message.html', {'message': message})


@method_decorator(login_required(login_url='/login'), name='dispatch')
class ResetUserView(View):
    '''
    更换邮箱发送验证码
    '''

    def post(self, request):
        email = request.POST.get('email')
        username = request.POST.get('username')
        if email and username:
            if User.objects.filter(email=email):
                return JsonResponse({'status': 400, 'message': '邮箱已经存在'})
            send_register_email.delay(email=email, username=username, send_type='update_email')
            return JsonResponse({'status': 200, 'message': u"验证码发送成功，有效期为30分钟"})
        return JsonResponse({'status': 400, 'message': '用户名与邮箱不能为空'})


@method_decorator(login_required(login_url='/login'), name='dispatch')
class EmailView(View):
    '''
    更换邮箱
    '''

    def post(self, request):
        forms = EmailForm(request.POST)
        if forms.is_valid():
            email = forms.cleaned_data.get('email')
            username = forms.cleaned_data.get('username')
            code = forms.cleaned_data.get('code')
            end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 1800))
            items = VerifyCode.objects.filter(send_time__lt=end_time)
            for item in items:
                item.delete()
            exitsed = VerifyCode.objects.filter(code__icontains=code, email=email, send_type='update_email')
            if exitsed:
                user = request.user
                user.email = email
                user.save()
                return JsonResponse({'status': 200, 'message': '修改成功,请重新登录'})
            else:
                return JsonResponse({'status': 400, 'message': '验证码已过期或错误'})
        return JsonResponse({'status': 400, 'message': '验证失败请检查后提交'})


@method_decorator(login_required(login_url='/login'), name='dispatch')
class Modify(View):
    '''
    密码修改
    '''

    def post(self, request):
        forms = ModifyForm(request.POST)
        if forms.is_valid():
            pwd1 = forms.cleaned_data.get('password')
            pwd2 = forms.cleaned_data.get('password1')
            email = forms.cleaned_data.get('email')
            if pwd1 != pwd2:
                return JsonResponse({'status': 400, "email": email, "message": "密码不一致"})
            is_user = User.objects.filter(email=email)
            if is_user:
                User.objects.filter(email=email).update(password=make_password(pwd2))
                return JsonResponse({'status': 200, "email": email, "message": "密码修改成功"})
            return JsonResponse({'status': 400, "email": email, "message": '邮箱不存在'})
        else:
            email = request.POST.get('email')
            return JsonResponse({'status': 400, "email": email, "message": '验证失败请检查后提交'})


class Retrieve(View):
    '''
    忘记密码
    '''

    def get(self, request):
        forms = ModifyForm()
        return render(request, 'pc/retrieve.html')

    def post(self, request):
        forms = ModifyForm(request.POST)
        if forms.is_valid():
            pwd1 = forms.cleaned_data.get('password')
            pwd2 = forms.cleaned_data.get('password1')
            email = forms.cleaned_data.get('email')
            captcha = request.POST.get('captcha', '')
            if captcha:
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 1800))
                if VerifyCode.objects.filter(email=email, code__icontains=captcha):
                    items = VerifyCode.objects.filter(email=email, code__icontains=captcha, send_time__lt=end_time)
                    for item in items:
                        item.delete()
                    exitsed = VerifyCode.objects.filter(code__icontains=captcha, email=email, send_type='forget')
                    if exitsed:
                        if pwd1 != pwd2:
                            return JsonResponse({

                                'status': 400,
                                'email': email,
                                'message': '密码不一致'
                            })
                        is_user = User.objects.filter(email=email)
                        if is_user:
                            User.objects.filter(email=email).update(password=make_password(pwd2))
                            for item in exitsed:
                                # 修改成功后是否删除该验证码保证30分钟内唯一性
                                item.delete()
                            return JsonResponse({
                                'status': 200,
                                'email': email,
                                'message': '密码修改成功'
                            })
                    else:
                        return JsonResponse({
                            'status': 400,
                            'email': email,
                            'message': '验证码已过期'
                        })
                else:
                    return JsonResponse({
                        'status': 400,
                        'email': email,
                        'message':
                            '验证码错误'
                    })
            return JsonResponse({
                'status': 400,
                'email': email,
                'message': '邮箱不存在'
            })
        else:
            email = request.POST.get('email')
            return JsonResponse({'status': 400, "email": email, "message": '验证失败请检查后提交'})


class RetrieveEmail(View):
    '''
    更换邮箱发送验证码
    '''

    def post(self, request):
        email = request.POST.get('email')
        if email:
            if User.objects.filter(email=email):
                send_register_email.delay(email=email, send_type='forget')
                return JsonResponse({
                    'status': 200,
                    'message': '验证码发送成功,有效期为30分钟'
                })
            return JsonResponse({'status': 400, 'message': u'邮箱不存在'})
        return JsonResponse({'status': 400, 'message': '邮箱不能为空'})


class Author(View):
    @method_decorator(login_required(login_url='/login'))
    def post(self, request):
        print(request.user.is_authenticated)
        if request.user.is_authenticated:
            forms = Follow_Forms(request.POST)
            username = request.POST.get('username')
            if forms.is_valid():
                follow = Follows()
                if request.POST.get('follow') == str(username):
                    return JsonResponse({
                        'status': 201,
                        'message': '不能自己关注自己'
                    })
                else:
                    cun = Follows.objects.filter(follow=forms.cleaned_data.get('follow'), fan=username)
                    if cun:
                        cun.delete()
                        return JsonResponse({
                            'status': 200,
                            'message': '已取消关注'
                        })
                    follow.follow = forms.cleaned_data.get('follow')
                    follow.fan_id = request.user.id
                    follow.save()
                    return JsonResponse({
                        'status': 200,
                        'message': '成功关注'
                    })
            else:
                return JsonResponse({
                    'status': 400,
                    'message': '失败'})
        else:
            return JsonResponse({
                'status': 403,
                'message': '请先登录'
            })


@method_decorator(login_required(login_url='/login'), name='dispatch')
class Person(View):
    '''个人中心'''

    @method_decorator(login_required(login_url='/login'), name='dispatch')
    def get(self, request):
        category = Category_Article.objects.all()
        count = User.objects.filter(follow__fan__id=request.user.id)
        follow = User.objects.filter(fan__follow_id=request.user.id)
        return render(request, 'pc/person/index.html', {'category': category, 'count': count, 'floow': follow})


class PersonDetaile(View):
    '''个人中心(他人)'''

    def get(self, request, article_id):
        category = Category_Article.objects.all()
        count = User.objects.filter(follow__fan__id=article_id)
        floow = User.objects.filter(fan__follow_id=article_id)
        user = User.objects.get(id=article_id)
        is_active = Follows.objects.filter(follow=article_id, fan=request.user.id).exists()
        if article_id == request.user.id:
            return redirect(reverse('user:person'))
        return render(request, 'pc/person/indexOthers.html',
                      {'category': category, 'count': count, 'floow': floow, 'user': user, 'is_active': is_active})


@login_required(login_url='/login')
def Profile(request):
    '''
    人脉
    :param request:
    :return:
    '''
    count = User.objects.filter(follow__fan__id=request.user.id)
    floow = User.objects.filter(fan__follow_id=request.user.id)
    user = User.objects.get(id=request.user.id)
    return render(request, 'pc/person/profile.html', {'count': count, 'floow': floow, 'user': user})


def ProfileOthers(request, article_id):
    '''
    人脉
    :param request:
    :param article_id:
    :return:
    '''
    category = Category_Article.objects.all()
    count = User.objects.filter(follow__fan__id=article_id)
    floow = User.objects.filter(fan__follow_id=article_id)
    user = User.objects.get(id=article_id)
    is_active = Follows.objects.filter(follow=article_id, fan=request.user.id).exists()
    return render(request, 'pc/person/profileOthers.html',
                  {'category': category, 'count': count, 'floow': floow, 'user': user, 'is_active': is_active})


@csrf_exempt
def Guan(request):
    '''
    取关
    :param request:
    :return:
    '''
    if request.method == 'POST':
        if request.user.id is not None:
            forms = Follow_Forms(request.POST)
            if forms.is_valid():
                floows = forms.cleaned_data.get('follow', '')
                user = request.POST.get('user', '')
                table = Follows.objects.filter(follow_id=floows, fan_id=user).delete()
                return JsonResponse({
                    'message': 'ok',
                    'data': 200
                })
        else:
            return JsonResponse({
                'message': '未登录'
            })
    return HttpResponse()


@login_required(login_url='/login')
def Info(request):
    '''
    资料修改
    :param request:
    :return:
    '''
    count = User.objects.filter(follow__fan__id=request.user.id)
    floow = User.objects.filter(fan__follow_id=request.user.id)
    user = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        forms = InfoForm(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data.get('username')
            mobile = forms.cleaned_data.get('mobile')
            info = request.POST.get('info')
            position = request.POST.get('position')
            file = request.FILES.get('file')
            user = request.user
            user.username = username
            user.mobile = mobile
            user.info = info
            user.position = position
            if file:
                user.user_imag = file
            user.save()
            return JsonResponse({
                'status': 200,
                'message': '修改成功'
            })
        return JsonResponse({
            'status': 400,
            'message': '提交失败'
        })
    return render(request, 'pc/person/info.html', {'count': count, 'floow': floow, 'user': user})


class InfoOthers(View):
    def get(self, request, article_id):
        category = Category_Article.objects.all()
        count = User.objects.filter(follow__fan__id=article_id)
        floow = User.objects.filter(fan__follow_id=article_id)
        user = User.objects.get(id=article_id)
        is_active = Follows.objects.filter(follow=article_id, fan=request.user.id).exists()
        return render(request, 'pc/person/infoOthers.html', {
            'category': category,
            'count': count,
            'floow': floow,
            'user': user,
            'is_active': is_active
        })


@login_required(login_url='login/')
def get_message(request):
    '''
    获取未读信息
    :param request:
    :return:
    '''
    count = UserMessage.objects.filter(user=request.user, has_read=False).count()
    return JsonResponse({
        'status': 200,
        'count': count
    })


@login_required(login_url='login/')
def message(request):
    '''
    消息
    :param request:
    :return:
    '''
    data = []
    if request.method == 'POST':
        type = request.POST.get('id', '')
        if type:
            UserMessage.objects.filter(id=type).update(has_read=True)
            return JsonResponse({
                'status': 200,
                'message': 'ok'
            })
        type = request.POST.get('type', '')
        if type == 'unread':
            message = UserMessage.objects.filter(user_id=request.user.id, has_read=False)
            for i in message:
                json_list = {}
                json_list['id'] = i.id
                json_list['message'] = i.message
                json_list['has_read'] = i.has_read
                json_list['is_supper'] = i.is_supper
                json_list['ids'] = i.ids
                json_list['add_time'] = i.add_time
                data.append(json_list)
            return JsonResponse({
                'status': 200,
                'message': data
            })
        elif type == 'read':
            message = UserMessage.objects.filter(user_id=request.user.id, has_read=True)
            for i in message:
                json_list = {}
                json_list['id'] = i.id
                json_list['message'] = i.message
                json_list['has_read'] = i.has_read
                json_list['is_supper'] = i.is_supper
                json_list['ids'] = i.ids
                json_list['add_time'] = i.add_time
                data.append(json_list)
            return JsonResponse({
                'status': 200,
                'message': data
            })
    return render(request, 'pc/person/message.html')


class PersonApiabstohr(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_show=True)
    serializer_class = ArticleSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = CategoryFilter
    authentication_classes = [
        SessionAuthentication,
        JSONWebTokenAuthentication]
    pagination_class = StandardResultsSetPagination


class PersonApi(PersonApiabstohr):
    '''
    个人中心
    '''
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问

    # def list(self, request, *args, **kwargs):
    #     queryset = Article_add.objects.filter(authors_id=self.request.user.id).order_by('-add_time')
    #     serializer = ArticleSerializer(queryset, many=True)
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     return Response(serializer.data)

    def get_queryset(self):
        '''
        this view should return a list of all the purchases
        for the currently authenticated user.
        :return:
        '''
        user = self.request.user
        # user_id = self.request.query_params.get('pk')
        # if user_id:
        #     return Article_add.objects.filter(authors_id=user_id).filter(is_show=True).order_by('-add_time')
        return Article.objects.filter(authors_id=self.request.user.id).filter(is_show=True).order_by('-add_time')


class PersonOthers(PersonApiabstohr):
    '''
    个人中心
    '''

    def get_queryset(self):
        '''
        this view should return a list of all the purchases
        for the currently authenticated user.
        :return:
        '''
        user_id = self.request.query_params.get('pk')
        if user_id:
            return Article.objects.filter(authors_id=user_id).filter(is_show=True).order_by('-add_time')


class UserGetAllInfo(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问
    authentication_classes = [
        SessionAuthentication,
        JSONWebTokenAuthentication
    ]
    pagination_class = StandardResultsSetPagination

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        type = request.data['type']
        if type:
            users = instance
            users.is_active = request.data['is_active']
            users.save()
            return Response({
                'id': users.id,
                'is_active': users.is_active
            })
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            '''
            if prefetch_related has been applied to a queryset,we need to forcibly invalidate the prefetch cache on the instance
            '''
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)


class UserGetInfo(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    '''
    list: 获取当前用户个人信息
    '''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问
    authentication_classes = [
        SessionAuthentication,
        JSONWebTokenAuthentication
    ]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        users = instance
        users.username = request.data['username']
        users.info = request.data['info']
        users.position = request.data['position']
        if request.data['list_pic']:
            users.user_imag = request.data['list_pic']
            users.save()
            return Response({"status": 'ok'})
        users.save()
        return Response({'success': 'ok'})


class UserMessages(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    '''
    消息
    '''
    queryset = UserMessage.objects.all()
    serializer_class = UserMessageSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问
    authentication_classes = [
        SessionAuthentication,
        JSONWebTokenAuthentication
    ]
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        if self.request.query_params.get('type'):
            type = self.request.query_params.get('type')
            if type == 'unread':
                queryset = UserMessage.objects.filter(
                    user=self.request.user, has_read=False
                )
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            elif type == 'read':
                queryset = UserMessage.objects.filter(user=self.request.user, has_read=True)
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if self.request.query_params.get('type'):
            type = self.request.query_params.get('type')
            if type == 'unread':
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                types = request.data['active']
                if types:
                    users = instance
                    users.has_read = request.data['active']
                    users.save()
                    return Response({'id': users.id, 'has_read': users.has_read})
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                return Response(serializer.data)


conf = ConfigParser()
conf.read('config.ini')
from django.shortcuts import HttpResponseRedirect
from urllib import parse
from urllib import request as req


def to_login(request):
    '''
    获取授权回调地址
    :param request:
    :return:
    '''
    next = request.GET.get('next', '')
    state = str(random.randrange(100000, 999999))
    # 定义一个随机状态码,防止跨域伪造攻击
    request.session['state'] = state
    # 将随机状态码存入session,用于授权信息返回时验证
    request.session['next'] = next
    client_id = conf.get('QQ', 'client_id')
    # qq互联中网站应用的APPID.
    callback = parse.urlencode({'redirect_uri': '127.0.0.1:8000/index'})
    # 对回调地址进行编码,用户同意授权后将调用此链接
    login_url = 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=%s&%s&state=%s&next=%s' % (
        client_id, callback, state, next)  # 组织QQ第三方登录链接
    return HttpResponseRedirect(login_url)
    # 重定向到qq第三方登录授权页面


def parse_jsonp(jsonp_str):
    '''
    解析返回数据
    :param jsonp_str:
    :return:
    '''
    try:
        return re.search('^[^(]*?\((.*)\)[^)]*$', jsonp_str).group(1)
    except:
        raise ValueError('无效数据!')


def qq(request):
    '''
    快捷qq登录获取token
    :param request:
    :return:
    '''
    # print(request.session['state'])
    if request.session['state'] == request.GET['state']:  # 验证状态码,防止跨域伪造攻击
        next = request.session['next']
        code = request.session['code']  # 获取用户授权码
        client_id = conf.get('QQ', 'client_id')
        # qq互联中网站应用的app id
        client_secret = conf.get('QQ', 'key')  # QQ互联中网站应用的APP Key。
        callback = parse.urlencode({'redirect_uri': '127.0.0.1:8000/qq'})
        # 对回调地址进行编码，用户同意授权后将调用此链接。
        login_url = 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&code=%s&client_id=%s&client_secret=%s&%s' % (
            code, client_id, client_secret, callback)  # 组织获取访问令牌的链接
        response = req.urlopen(login_url).read().decode()  # 打开获取访问令牌的链接
        try:
            access_token = re.split('&', response)[0]  # 获取访问令牌
            res = req.urlopen('https://graph.qq.com/oauth2.0/me?' + access_token).read().decode()  # 打开获取openid的连接
            openid = json.loads(parse_jsonp(res))['openid']  # 从返回数据中获取openid
            userinfo = req.urlopen('https://graph.qq.com/user/get_user_info?oauth_consumer_key=%s&openid=%s&%s' % (
                client_id, openid, access_token)).read().decode()  # 打开获取用户信息的连接
            userinfo = json.loads(userinfo)  # 将返回的用户信息数据（JSON格式）读取为字典。
            figureurl_qq_1 = userinfo['figureurl_qq_1']  # 新用户头像
            nickname = userinfo['nickname']
            authqq = OAuthQQ.objects.filter(qq_openid=openid)
            if not authqq:
                return render(request, 'pc/qqregister.html',
                              {'openid': openid, 'figureurl_qq_1': figureurl_qq_1, 'nickname': nickname, 'next': next})
            else:
                user = authqq[0].user
                login(request, user)
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect(reverse('home'))
        except Exception as e:
            raise ValueError(e)
    else:
        raise ValueError('授权失败,请稍后重试')


def getClbackQQ(request):
    '''
    获取授权回调地址
    :param request:
    :return:
    '''
    next = request.GET.get('next', '')
    state = str(random.randrange(100000, 999999))
    # 定义一个随机状态码,防止跨域伪造攻击.
    request.session['state'] = state
    # 将随机状态码存入session,用于授权信息返回时验证.
    request.session['next'] = next
    client_id = '101532677'
    # qq互联中网站应用的app id
    callback = parse.urlencode({
        'redirect_uri': '127.0.0.1:8000/callbackget'
    })
    # 对毁掉地址进行编码,用户同意授权后将调用此链接
    login_url = 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=%s&%s&state=%s&next=%s' % (
        client_id, callback, state, next)  # 组织QQ第三方登录链接
    return HttpResponseRedirect(login_url)  # 重定向到QQ第三方登录授权页面


def getClback(request):
    '''
    获取token
    :param request:
    :return:
    '''
    if request.session['state'] == request.GET['state']:  # 验证状态码,防止跨域伪造攻击
        next = request.session['next']
        code = request.GET['code']  # 获取用户授权码
        client_id = conf.get('QQ', 'client_id')
        # QQ互联中网站应用的APP ID。
        client_secret = conf.get('QQ', 'key')  # QQ互联中网站应用的APP Key。
        callback = parse.urlencode({'redirect_uri': '127.0.0.1:8000/callbackget'})
        # 对回调地址进行编码，用户同意授权后将调用此链接。
        login_url = 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&code=%s&client_id=%s&client_secret=%s&%s' % (
            code, client_id, client_secret, callback)  # 组织获取访问令牌的链接
        response = req.urlopen(login_url).read().decode()  # 打开获取访问令牌的链接
        try:
            access_token = re.split('&', response)[0]  # 获取访问令牌
            res = req.urlopen('https://graph.qq.com/oauth2.0/me?' + access_token).read().decode()  # 打开获取openid的链接
            openid = json.loads(parse_jsonp(res))['openid']  # 从返回数据中获取openid
            userinfo = req.urlopen('https://graph.qq.com/user/get_user_info?oauth_consumer_key=%s&openid=%s&%s' % (
                client_id, openid, access_token)).read().decode()  # 打开获取用户信息的链接
            userinfo = json.loads(userinfo)  # 将返回的用户信息数据（JSON格式）读取为字典。
            figureurl_qq_1 = userinfo['figureurl_qq_1']  # 新用户头像
            nickname = userinfo['nickname']
            authqq = OAuthQQ.objects.filter(qq_openid=openid)
            if authqq.exists():
                raise ValueError('qq已绑定')
            else:
                OAuthQQ.objects.create(qq_openid=openid, nickname=nickname, user_id=request.user.id)
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect(reverse('home'))
        except Exception:
            raise ValueError('user不存在请联系管理员')
    else:
        raise ValueError('授权失败,请稍后重试')


def bindingQQ(request):
    '''
    qq 注册账号
    :param request:
    :return:
    '''
    if request.method == 'POST':
        openid = request.POST.get('openid')
        figureurl_qq_1 = request.POST.get('figureurl_qq_1')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        email = request.POST.get('email')
        if password != password1:
            return render(request, 'pc/qqregister.html',
                          {'openid': openid, 'figureurl_qq_1': figureurl_qq_1, 'nickname': nickname,
                           'error': '两次密码不一致'})

        else:
            if User.objects.filter(email=email).exists():
                return render(request, 'pc/qqregister.html',
                              {'openid': openid, 'figureurl_qq_1': figureurl_qq_1, 'nickname': nickname,
                               'error': '邮箱已存在'})
            else:
                user = User()
                user.username = nickname
                user.email = email
                user.user_image = figureurl_qq_1
                user.is_staff = False
                user.is_superuser = False
                user.is_active = True
                user.password = make_password(password1)
                user.save()
                qq = OAuthQQ()
                user_id = get_object_or_404(User, email=email).id
                qq.user_id = user_id
                msg = UserMessage()
                msg.user_id = user_id
                msg.to_user = User.objects.get(is_superuser=True)
                msg.message = '欢迎加入本站,在使用过程中有什么疑问,请联系管理员,Email: <a target="_blank" href="http://mail.qq.com/cgi-bin/qm_share?t=qm_mailme&email=iuzv5O3g4_T748rs7_Tt4OPk__Ok6eXn" style="text-decoration:none;">fengjinqi@fengjinqi.com</a>'
                msg.has_read = False
                msg.is_supper = True
                msg.save()
                qq.qq_openid = openid
                qq.nickname = nickname
                qq.figureurl_qq = figureurl_qq_1
                qq.save()
                user = authenticate(request, username=email, password=password)
                login(request, user)
                return HttpResponseRedirect(reverse('home'))


