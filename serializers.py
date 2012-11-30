from django.forms import widgets
from django.contrib.auth.models import User
from rest_framework import serializers
from tmg import models

class ProcessSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.Field(source='owner.username')
    parameters = serializers.CharField(required=False)

    id = serializers.CharField(source='pk', read_only=True)
    task_id = serializers.CharField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    started_on = serializers.DateTimeField(read_only=True)
    finished_on = serializers.DateTimeField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    progress = serializers.IntegerField(read_only=True)
    eta = serializers.CharField(read_only=True)

    class Meta:
        model = models.Process
        fields = ('id', 'owner', 'source', 'operation', 'parameters', 'task_id', 'created_on', 'started_on', 'finished_on', 'status', 'progress', 'eta')
