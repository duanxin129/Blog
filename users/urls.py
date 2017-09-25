from django.conf.urls import url
from django.conf import  settings

from . import views

app_name = 'users'
urlpatterns=[
    url(r'register/',views.register,name='register'),
]