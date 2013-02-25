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
from django.forms import widgets
from django.contrib.auth.models import User
from rest_framework import serializers
from tmg import models

class ProcessSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.Field(source='owner.username')

    operation = serializers.ChoiceField(choices=models.operations.list_registered_operations())
    parameters = serializers.CharField(required=False)

    id = serializers.CharField(source='pk', read_only=True)
    output = serializers.CharField(read_only=True)
    task_id = serializers.CharField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    started_on = serializers.DateTimeField(read_only=True)
    finished_on = serializers.DateTimeField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    progress = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Process
        fields = ('id', 'url', 'owner', 'source', 'operation', 'parameters', 'task_id', 'created_on', 'started_on', 'finished_on', 'status', 'progress', 'output')
