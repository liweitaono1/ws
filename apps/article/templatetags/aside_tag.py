from django import template

from article.models import Article

register = template.Library()
@register.inclusion_tag('pc/base_aside.html')
def get_aside():
    popular = Article.objects.filter(is_show=True).order_by('-click_nums')[:5]
    return {'popular': popular}


@register.simple_tag
def get_categories():
    return Article.objects.filter(is_show=True).order_by('-click_nums')[:5]