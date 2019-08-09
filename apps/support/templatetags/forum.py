from datetime import datetime

from django.contrib.sessions.models import Session
from django.utils.timezone import now, timedelta
from django import template
from django.contrib.auth import get_user_model

from support.models import QQ
from forum.models import Forum

register = template.Library()

User = get_user_model()


@register.inclusion_tag('pc/aside/forum_side.html')
def get_fourm():
    qq = QQ.objects.all()
    fourm = Forum.objects.filter(category__name='求职招聘')[:10]
    sessions = Session.objects.filter(expire_date__gte=datetime.now()).count()
    user = User.objects.count()
    cur_date = now().date() + timedelta(days=0)
    days = Forum.objects.filter(add_time__gte=cur_date).count()
    count = Forum.objects.count()
    Hottest = Forum.objects.order_by('-click_nums')[:10]
    return {'fourm': fourm, 'qq': qq, 'user': user, 'sessions': sessions, 'days': days, 'count': count,
            'Hottest': Hottest}
