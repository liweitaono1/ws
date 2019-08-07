import os
from celery import Celery, platforms
from django.conf import settings

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'website.settings'
)
platforms.C_FORCE_ROOT = True
app = Celery('website')

app.config_from_object('django.conf:settings')

# celery会自动在你注册app中寻找tasks
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
