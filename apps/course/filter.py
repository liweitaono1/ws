import django_filters

from course.models import Courses


class CoursesFilter(django_filters.rest_framework.FilterSet):
    title = django_filters.rest_framework.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Courses
        fields = ['title', ]
