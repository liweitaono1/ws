import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Create your models here.

class Forum_plate(models.Model):
    '''
    论坛版块表
    '''


class Forum(models.Model):
    '''帖子表'''
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    keywords = models.CharField(max_length=200, verbose_name='关键字', default='', blank=True, null=True)
    category = models.ForeignKey(Forum_plate, verbose_name='版块名称', on_delete=models.CASCADE)
    content = models.TextField(u'内容')
    click_nums = models.PositiveIntegerField(default=0, verbose_name='阅读数量')
    authors = models.ForeignKey(User, verbose_name="作者", on_delete=models.CASCADE)
    # 发布日期
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="发布日期")
    # 是否关闭
    hidden = models.BooleanField(default=False, verbose_name="是否隐藏")

    def __str__(self):
        return self.title

    def get_number(self):
        n = self.comment_set.all()
        num = self.comment_set.all().count()
        for i in n:
            num += i.parent_comment_set.count()
        return num

    class Meta:
        verbose_name = '帖子表'
        verbose_name_plural = verbose_name
        ordering = ('-add_time',)
