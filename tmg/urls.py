#
# Copyright Olivier Aubert <contact@olivieraubert.net> 2013
#
# This software offers a media transcoding and processing platform.
#
# TMG is a free software subjected to a double license.
# You can redistribute it and/or modify if you respect the terms of either
# (at least one of both licenses):
# - the GNU Lesser General Public License as published by the Free Software Foundation;
#   either version 3 of the License, or any later version.
# - the CeCILL-C as published by CeCILL; either version 2 of the License, or any later version.
#
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
                        url(r'^cleanup$', views.cleanup),
                        )

