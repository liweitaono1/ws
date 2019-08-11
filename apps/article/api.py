from django.db.models.signals import post_save
from django.dispatch import receiver
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from article.filter import ArticleFilter
from article.models import Recommend, Category_Article, ArticleCommentReply, Article_Comment, Article
from article.serializers import ArticleCommitSerializer, Category_ArticleSerializer, Article_CommentSerializerAdd, \
    ArticleCreatedSerializer, ArticleSerializer,ArticleCommentReplySerializer
from article.views import StandardResultsSetPagination
from user.models import UserMessage
from utils.permissions import IsOwnerOrReadOnly, IsOwnerOr, CsrfExemptSessionAuthentication


class ArticleListView(viewsets.ReadOnlyModelViewSet):
    """
     TODO 列出所有的文章 详情页
    """
    queryset = Article.objects.filter(is_show=True).order_by('-add_time')
    serializer_class = ArticleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = ArticleFilter
    permission_classes = (IsAuthenticated, IsOwnerOr)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]

class MeArticleListView(viewsets.ReadOnlyModelViewSet):
    """
     TODO 我的的文章 详情页
    """
    queryset = Article.objects.filter(is_show=True).order_by('-add_time')
    serializer_class = ArticleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = ArticleFilter
    permission_classes = (IsAuthenticated, IsOwnerOr)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]

    def get_queryset(self):
        return Article.objects.filter(authors_id=self.request.user.id).filter(is_show=True).order_by(
            '-add_time')



class FollowListView(viewsets.ReadOnlyModelViewSet):
    """
    TODO 我关注的文章
    """
    queryset = Article.objects.filter(is_show=True).order_by('-add_time')
    serializer_class = ArticleSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated, IsOwnerOr)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]
    def list(self, request, *args, **kwargs):

        queryset = Article.objects.filter(authors__follow__fan_id=self.request.user.id).filter(is_show=True).order_by('-add_time')
        serializer = ArticleSerializer(queryset, many=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class ArticleCreated(mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    """
    创建文章
    """
    queryset = Article.objects.filter(is_show=True)
    serializer_class = ArticleCreatedSerializer
    permission_classes = (IsAuthenticated,IsOwnerOr)  # 未登录禁止访问
    authentication_classes = [CsrfExemptSessionAuthentication, JSONWebTokenAuthentication]



class ArticleCommintView(mixins.CreateModelMixin,viewsets.ReadOnlyModelViewSet):
    """TODO 評論"""
    serializer_class = Article_CommentSerializerAdd
    queryset = Article_Comment.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]


@receiver(post_save, sender=Article_Comment)
def my_callback(sender, **kwargs):
    """
    评论通知
    :param sender:
    :param kwargs:
    :return:
    """

    message = UserMessage()
    message.user=kwargs['instance'].article.authors
    message.ids = kwargs['instance'].article.id
    message.to_user_id = kwargs['instance'].user_id
    message.has_read = False
    message.url =kwargs['instance'].url
    message.message="你的%s文章被人评论了,快去看看吧!"%kwargs['instance'].article.title
    message.save()


class ArticleCommentReplyView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    """TODO 回復評論"""
    serializer_class = ArticleCommentReplySerializer
    queryset = ArticleCommentReply.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]
@receiver(post_save, sender=ArticleCommentReply)
def my_callback_reply(sender,**kwargs):
    '''
    评论通知
    :param sender:
    :param kwargs:
    :return:
    '''
    message = UserMessage()
    message.user = kwargs['instance'].to_uids
    message.ids = kwargs['instance'].aomments_id.article.id
    message.to_user = kwargs['instance'].user
    message.has_read = False
    message.url = kwargs['instance'].url
    message.message = "你参与的 %s 文章评论有人回复了,快去看看吧!" % kwargs['instance'].aomments_id.article.title
    message.save()

class CategoryView(mixins.UpdateModelMixin,mixins.CreateModelMixin,viewsets.ReadOnlyModelViewSet):
    """TODO 分類"""
    queryset = Category_Article.objects.all()
    serializer_class = Category_ArticleSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问
    authentication_classes = [CsrfExemptSessionAuthentication, JSONWebTokenAuthentication]

class ArticleCommit(viewsets.ModelViewSet):
    """文章推荐"""
    queryset = Recommend.objects.filter(is_recommend=True)
    serializer_class = ArticleCommitSerializer
    permission_classes = (IsAuthenticated,)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]