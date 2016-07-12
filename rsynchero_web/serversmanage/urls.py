from django.conf.urls import url
from . import views

app_name = 'serversmanage'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^server/(?P<pk>[0-9]+)/$', views.ServerInfo.as_view(), name='serverinfo'),
    url(r'^serveradd/$', views.ServerAdd.as_view(), name='serveradd'),
    url(r'^server/(?P<pk>[0-9]+)/edit/$', views.ServerUpdate.as_view(), name='serveredit'),
    url(r'^server/(?P<pk>[0-9]+)/delete/$', views.ServerDelete.as_view(), name='serverdelete'),
]