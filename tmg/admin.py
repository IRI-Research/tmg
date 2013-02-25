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
