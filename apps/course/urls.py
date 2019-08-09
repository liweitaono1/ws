from django.urls import path
from . import views

app_name = '[course]'

urlpatterns = [
    path('', views.List, name='index'),
    path('<uuid:course_id>/<str:list_id>.html/', views.Detail, name='detail'),

    path('api/<uuid:courses_id>/', views.courseViewApi, name='courseViewApi'),
]
