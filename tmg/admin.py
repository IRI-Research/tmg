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
from django.contrib import admin, messages
from models import Process

class ProcessAdmin(admin.ModelAdmin):
    class Meta:
        model = Process

    fields = ('source', 'operation', 'parameters')
    list_display = ('id', 'owner', 'source', 'operation', 'parameters',
                    'task_id', 'created_on', 'started_on', 'finished_on',
                    'status', 'progress')
    readonly_fields = ('id', 'owner',
                       'task_id', 'created_on', 'started_on', 'finished_on',
                       'status', 'progress')
    list_filter = ('status','source', 'operation',)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.save()

admin.site.register(Process, ProcessAdmin)
