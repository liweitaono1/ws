from django.urls import path

from article import views

app_name = '[article]'
urlpatterns = [

  path('created/',views.Article_Add,name='created'),

  path('',views.ArticleList,name='index'),
  path('me/',views.ArticleMe,name='me'),
  path('blog_img_upload/',views.blog_img_upload,name='blog_img_upload'),
  path('detail/<uuid:article_id>',views.Article_detail,name='detail'),
  path('update/<uuid:article_id>',views.ArticleUpdate,name='update'),
  path('update_image/<uuid:article_id>',views.RemoveImage,name='update_image'),
  path('delete/',views.ArticleDelete,name='delete'),
  path('api/',views.api,name='api'),
  path('apis/',views.addModel),

]