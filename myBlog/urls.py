from django.conf.urls import url,include
from django.contrib.auth.decorators import login_required

from . import views




# regular expression
app_name = 'blog'
urlpatterns = [
    url(r'^$',views.IndexView.as_view(),name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$',login_required(views.PostDetailView.as_view()),name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',views.ArchivesView.as_view(),name='archives'),
    url(r'^category/(?P<pk>[0-9]+)/$',views.CategoryView.as_view(),name='category'),
    url(r'^tag/(?P<pk>[0-9]+)/$',views.TagView.as_view(),name='tag'),
    url(r'^report/$',views.report,name='report'),
    url(r'^save/$',views.saveArticle,name='save'),


]