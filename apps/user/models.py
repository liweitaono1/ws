import uuid
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class User(AbstractUser):
    # id = ShortUUIDField(primary_key=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, blank=True, null=True, verbose_name='姓名')
    mobile = models.CharField(max_length=11, verbose_name='手机号码', default='')
    position = models.CharField(max_length=30, verbose_name='职位', default='', null=True, blank=True)
    info = models.CharField(max_length=100, verbose_name='个人介绍', default='', null=True, blank=True)
    user_imag = models.ImageField(upload_to='user/%Y%m%d', blank=True, null=True, default='', verbose_name='用户头像')
    user_image = models.URLField(default='', null=True, blank=True)
    email = models.EmailField(unique=True, default='')

    def get_qq(self):
        if self.oauthqq_set.get(user=self):
            return True
        else:
            return False

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class OAuthQQ(models.Model):
    '''
    qq
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100)
    qq_openid = models.CharField(max_length=100)
    figureurl_qq = models.URLField()


class Follows(models.Model):
    '''
    关注表
    '''
    follow = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow', verbose_name='被关注的,作者')
    fan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fan', verbose_name='粉丝')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    def __str__(self):
        return str(self.follow.id)

    class Meta:
        ordering = ('-follow',)


class VerifyCode(models.Model):
    '''
    邮箱验证码
    '''
    code = models.CharField(verbose_name='验证码', max_length=10)
    mobile = models.CharField(blank=True, null=True, verbose_name='电话', max_length=11)
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')
    email = models.EmailField(verbose_name='邮箱', default='')
    send_choices = (
        ('register', '注册'),
        ('forget', '找回密码'),
        ('update_email', '修改密码')
    )
    send_type = models.CharField(verbose_name='验证码类型', max_length=30, choices=send_choices, default='register')
    send_time = models.DateTimeField(default=datetime.now, verbose_name='发送时间')

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = verbose_name


class UserMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', verbose_name='收消息用户')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user', verbose_name='发消息用户', null=True,
                                blank=True)
    message = models.TextField(verbose_name='消息内容')
    ids = models.UUIDField(blank=True, null=True, verbose_name='评论文章id')
    url = models.CharField(max_length=200, verbose_name='地址', null=True, blank=True)
    is_supper = models.BooleanField(default=False, verbose_name='是系统消息')
    has_read = models.BooleanField(default=False, verbose_name='是否已读')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name
        ordering = ('-add_time',)
