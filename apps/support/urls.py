from django.urls import path

app_name='support'
from . import views
urlpatterns = [
    # path('',views.login_view,name='index'),
    path('', views.index, name='support'),
]