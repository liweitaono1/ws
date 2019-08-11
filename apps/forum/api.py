from django.db.models.signals import post_save
from django.dispatch import receiver
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from forum.serializers import Forum_plateSerializers, ForumSerializers, CommentSerializers, \
    Pernents_CommentSerializers
from article.views import StandardResultsSetPagination
from forum.filter import ForumFilter
from forum.models import Parent_Comment, Comment, Forum, Forum_plate
from user.models import UserMessage
from utils.permissions import IsOwnerOrReadOnly, IsOwnerOr


class Forum_plateView(mixins.UpdateModelMixin,mixins.CreateModelMixin,viewsets.ReadOnlyModelViewSet):
    """TODO 版块分類"""
    queryset = Forum_plate.objects.all()
    serializer_class = Forum_plateSerializers
    permission_classes = (IsAuthenticated, IsOwnerOr)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]


class ForumView(viewsets.ModelViewSet):
    """TODO 帖子"""
    queryset = Forum.objects.filter(hidden=False)
    serializer_class = ForumSerializers
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated, IsOwnerOr)  # 未登录禁止访问
    filter_backends = (DjangoFilterBackend,)
    filter_class = ForumFilter
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]

    def get_queryset(self):
        if self.request.user.is_superuser and self.request.user:
            return Forum.objects.filter(hidden=False)
        else:
            return Forum.objects.filter(authors=self.request.user)



class CommentView(viewsets.ModelViewSet):
    """TODO 评论"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializers
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]


@receiver(post_save, sender=Comment)
def my_callback(sender, **kwargs):
    """
    评论通知
    :param sender:
    :param kwargs:
    :return:
    """
    message = UserMessage()
    message.user=kwargs['instance'].forums.authors
    message.ids = kwargs['instance'].forums.id
    message.to_user_id = kwargs['instance'].user_id
    message.has_read = False
    message.url =kwargs['instance'].url
    message.message="你的%s帖子被人评论了,快去看看吧!"%kwargs['instance'].forums.title
    message.save()




class Parent_CommentView(viewsets.ModelViewSet):
    """TODO 评论回复"""
    queryset = Parent_Comment.objects.all()
    serializer_class = Pernents_CommentSerializers
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 未登录禁止访问
    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]
