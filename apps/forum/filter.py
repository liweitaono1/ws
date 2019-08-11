import django_filters

from forum.models import Forum


class ForumFilter(django_filters.rest_framework.FilterSet):
    category = django_filters.rest_framework.BaseInFilter(field_name='category_id')
    title = django_filters.rest_framework.CharFilter(field_name='title',lookup_expr='icontains')
    class Meta:
        model = Forum
        fields = ['category','title']