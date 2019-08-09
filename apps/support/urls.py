from django.urls import path

app_name='support'
from . import views
urlpatterns = [
    path('', views.index, name='support'),
]