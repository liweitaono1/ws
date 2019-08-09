from django.contrib.auth import get_user_model
from rest_framework import serializers

from course.models import CourseList, Courses

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'user_imag', 'id')


class AddtutorialSerializers(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)

    class Meta:
        model = CourseList
        fields = '__all__'


class CourseSerializers(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    image = serializers.ImageField(required=False)
    user = UserSerializer(read_only=True)
    courselist_set = AddtutorialSerializers(many=True)

    class Meta:
        model = Courses
        fields = '__all__'


class CreatedCourseSerializers(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'
