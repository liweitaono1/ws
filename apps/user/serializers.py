from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import UserMessage

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        # 自定义序列化数据返回
        res = super(UserSerializer, self).to_representation(instance=instance)
        access = []
        if res['is_staff'] == True:
            access.append('is_staff')
        if res['is_superuser'] == True:
            access.append('is_superuser')
        res.setdefault('access', access)
        return res

    class Meta:
        model = User
        fields = (
            'id', 'username', 'mobile', 'user_imag', 'user_image', 'email', 'is_active', 'is_staff', 'is_superuser',
            'info',
            'position')


class UserMessageSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    class Meta:
        model = UserMessage
        fields = '__all__'
