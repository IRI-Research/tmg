from tmg.models import Process
from tmg.serializers import ProcessSerializer
from tmg.permissions import IsOwnerOrReadOnly

from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
            'process': reverse('process-list', request=request),
            })

@api_view(('POST',))
def cleanup(request, format=None):
    Process.cleanup_expired_processes(ignore_state=('force' in request.GET))
    return Response({
            'process': reverse('process-list', request=request),
            })

class ProcessList(generics.ListCreateAPIView):
    model = Process
    serializer_class = ProcessSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user

    def delete(self, request, *args, **kwargs):
        Process.cleanup_expired_processes(ignore_state=('force' in request.GET))
        return Response({
                'process': reverse('process-list', request=request),
                })

class ProcessDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Process
    serializer_class = ProcessSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user
