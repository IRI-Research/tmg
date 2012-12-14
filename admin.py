from django.contrib import admin, messages
from models import Process

class ProcessAdmin(admin.ModelAdmin):
    class Meta:
        model = Process

    list_display = ('id', 'owner', 'source', 'operation', 'parameters',
                    'task_id', 'created_on', 'started_on', 'finished_on',
                    'status', 'progress', 'eta')
    list_display_links = ('id', )
    readonly_fields = ('id', 'owner',
                       'task_id', 'created_on', 'started_on', 'finished_on',
                       'status', 'progress', 'eta')
    list_filter = ('status','source', 'operation',)

admin.site.register(Process, ProcessAdmin)
