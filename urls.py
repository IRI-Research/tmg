from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from tmg import views

urlpatterns = patterns('',
                       url(r'^process/$', views.ProcessList.as_view(), name='process-list'),
                       url(r'^process/(?P<pk>[0-9]+)/$', views.ProcessDetail.as_view(), name='process-detail'), 
                       )

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += patterns('',
                        url(r'^api-auth/', include('rest_framework.urls',
                                                   namespace='rest_framework')),
                        url(r'^$', views.api_root),
                        )

