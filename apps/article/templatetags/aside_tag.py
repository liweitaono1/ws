from django import template


register = template.Library()
@register.inclusion_tag('pc/base_aside.html')
def get_aside():
    popular = Article.objects.filter(is_show=True).order_by('-click_nums')[:5]
    return {'popular': popular}