from django.urls import path
from apps.forum.views import indexMe
from user import views

app_name = '[user]'

urlpatterns = [
    # path('',views.login_view,name='index'),
    path('', views.Person.as_view(), name='person'),
    path('author/', views.Author.as_view(), name='author'),
    path('<uuid:article_id>/', views.PersonDetaile.as_view(), name='author_detaile'),
    path('info/<uuid:article_id>/', views.InfoOthers.as_view(), name='info'),
    path('ProfileOthers/<uuid:article_id>/', views.ProfileOthers, name='ProfileOthers'),
    path('profile/', views.Profile, name='profile'),
    path('info/', views.Info, name='info'),
    path('forum/', indexMe, name='forum'),
    path('modify/', views.Modify.as_view(), name='modify'),
    path('retrieve/', views.Retrieve.as_view(), name='retrieve '),
    path('sing_email/', views.ResetUserView.as_view(), name='sing_email'),
    path('email_update/', views.EmailView.as_view(), name='email_update'),
    path('Guan/', views.Guan, name='Guan'),
    path('retrieveEmail/', views.RetrieveEmail.as_view(), name='retrieveEmail'),
    path('message/', views.message, name='message'),
    path('bindingQQ/', views.bindingQQ, name='bindingQQ'),
]
