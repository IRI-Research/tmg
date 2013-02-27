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
import json
import os
import sys
from datetime import datetime

from celery.decorators import task
from celery import current_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from django.conf import settings

from tmg import operations
from .models import Process
from .states import PROGRESS

REGISTERED_TASKS = {}

# The 'tmg' queue is meant to be run on workers that have access to
# the Django DB, so that they can update state information.
@task(name="tmg.success_callback", queue='tmg', ignore_result=True)
def success_callback(result):
    logger.info(u"Success callback %s" % unicode(result))
    p = Process.objects.get(pk=result['process'])
    result.pop('process')
    p.output = result
    p.status = p.FINISHED
    p.finished_on = datetime.now()
    p.save()

@task(name="tmg.failure_callback", queue='tmg', ignore_result=True)
def failure_callback(uuid):
    logger.info(u"Failure callback for %s" % unicode(uuid))
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    ps = Process.objects.filter(task_id=uuid)
    if len(ps) != 1:
        # FIXME: oops...
        logger.error("Cannot find Process associated to task %s" % uuid)
    else:
        p = ps[0]
        p.output = {'traceback': result.traceback}
        p.state = p.ABORTED
        p.save()

# Generic task method: it will not be registered by itself, but
# instead will be registered for every defined operation.  Since we
# pass the operation name as parameter in the json representation, we
# can instanciate and run the appropriate operation here.
def start_process(process_as_json_string):
    ret = None
    proc = json.loads(process_as_json_string)
    logger.info("Starting process %s %s" % (proc['id'], current_task.backend))

    def progress_callback(value=0, label=None):
        current_task.update_state(state=PROGRESS,
                                  meta={ 'process': proc.get('id'),
                                         'value': value,
                                         'label': label })

    opclass = operations.REGISTERED_OPERATIONS[proc.get('operation')]
    op = opclass(source=os.path.join(getattr(settings, 'MEDIA_ROOT', ''),
                                     proc.get('source')),
                 destination=proc.get('destination'),
                 parameters=proc.get('parameters') or {},
                 progress_callback=progress_callback)
    ret = op.start()
    logger.info("Finished process %s" % proc.get('id'))
    # Augment task output with process id
    ret['process'] = proc.get('id')
    return ret

# Define operations as tasks: For every opclass, define a dynamic
# op.method that will instanciate the opclass with the deserialized
# json parameters
for opname in operations.REGISTERED_OPERATIONS:
    REGISTERED_TASKS[opname] = task(name="tmg." + opname,
                                    track_started=True)(start_process)
