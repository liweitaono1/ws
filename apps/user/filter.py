import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from article.models import Article

User = get_user_model()


class CategoryFilter(django_filters.rest_framework.FilterSet):
    category = django_filters.rest_framework.CharFilter(field_name='category__id', lookup_expr='icontains')
    title = django_filters.rest_framework.CharFilter(field_name='title', lookup_expr='icontains')
    top_category = django_filters.rest_framework.NumberFilter(method='top_category_filter')

    def top_category_filter(self, queryset, name, value):
        print(queryset, name, value)
        queryset = queryset.filter(Q(category_id=value) | Q(category=value))
        return queryset

    class Meta:
        model = Article
        fields = ['category', 'title']


class UserFilter(django_filters.rest_framework.FilterSet):
    category = django_filters.rest_framework.CharFilter(field_name='id', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['category', ]
