from datetime import datetime

from celery import current_task
from celery.decorators import task
from celery.utils.log import get_task_logger

from tmg.models import Process

logger = get_task_logger(__name__)

@task
def start_process(pid, callback=None):
    proc = Process.objects.get(pk=pid)
    logger.info("Starting process %s" % proc)

    try:
        logger.info("------ running %s" % proc)
        proc.task_id = current_task.request.id

        proc.status = proc.STARTED
        proc.started_on = datetime.now()
        proc.save()

        proc.start()

        proc.status = proc.FINISHED
        proc.finished_on = datetime.now()
        proc.save()

        logger.info("Finished process %s" % proc)
    except Exception, e:
        logger.info("Failed process %s: %s" % (proc, unicode(e)))
        # FIXME: log reason in the DB ?
        proc.status = proc.ABORTED
        proc.finished_on = datetime.now()
        proc.save()

    #if callback:
    #    subtask(callback).delay(proc.pk)
    return True
