from rest_framework import serializers

from article.serializers import UserSerializer
from forum.models import Forum_plate, Forum, Comment, Parent_Comment

class Forum_plateSerializers(serializers.ModelSerializer):
    authors = UserSerializer(read_only=True)
    add_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = Forum_plate
        fields ='__all__'




class Pernents_CommentSerializers1(serializers.ModelSerializer):
    """
    评论回复
    """
    class Meta:
        model = Parent_Comment
        fields = '__all__'

class CommentSerializers1(serializers.ModelSerializer):
    """
    评论
    """
    parent_comment_set=Pernents_CommentSerializers1(many=True)
    class Meta:
        model = Comment
        fields = '__all__'



class ForumSerializers(serializers.ModelSerializer):
    """帖子"""
    authors = UserSerializer(read_only=True)
    category = Forum_plateSerializers(read_only=True)
    comment_set = CommentSerializers1(many=True)
    add_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Forum
        fields ='__all__'




class CommentSerializers(serializers.ModelSerializer):
    """
    评论
    """
    class Meta:
        model = Comment
        fields = '__all__'


class Pernents_CommentSerializers(serializers.ModelSerializer):
    """
    评论回复
    """
    parent_comments = CommentSerializers()
    class Meta:
        model = Parent_Comment
        fields = '__all__'