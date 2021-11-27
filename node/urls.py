from django.conf.urls import url

from node import views

urlpatterns = [
    url(r'^$', views.index, name='node'),
]
