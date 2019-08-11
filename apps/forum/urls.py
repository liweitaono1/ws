from django.urls import path

app_name='[forum]'
from . import views
urlpatterns = [
  path('',views.index,name='forum'),
  path('add/',views.add_forum,name='add'),
  path('detail/<uuid:forum_id>/',views.forum_detail,name='detail'),
  path('cagetory/<int:category>/',views.forum_category,name='id'),
  path('del/<uuid:id>/',views.delForum,name='del'),
  ]
