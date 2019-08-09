from django.urls import path

from article import views

app_name = '[article]'
urlpatterns = [
    path('', views.ArticleList, name='index'),
    path('created/', views.Article_Add, name='created'),
]
